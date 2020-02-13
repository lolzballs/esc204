#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/timerfd.h>
#include <time.h>
#include <unistd.h>

#define handle_error(msg) \
    do { perror(msg); exit(EXIT_FAILURE); } while (0)

#define POLL_STDIN 0
#define POLL_STDOUT 1
#define POLL_TIMER 2

#define BUFFER_MAX 1024

struct stepperd_buffer {
    uint8_t buf[BUFFER_MAX];
    size_t pos;
};

struct stepperd {
    struct stepperd_buffer input_buffer;
    struct stepperd_buffer output_buffer;
    
    int efd, tfd; 
};

void itimerspec_dump(struct itimerspec *ts);

int setup_timer(int usec) {
    int fd = timerfd_create(CLOCK_REALTIME, TFD_NONBLOCK);
    if (fd == -1)
        handle_error("timerfd_create");

    struct itimerspec timerspec = {
        .it_interval = {
            .tv_sec = usec / 1000000,
            .tv_nsec = (usec % 1000000) * 1000
        },
        .it_value = {
            .tv_sec = usec / 1000000,
            .tv_nsec = (usec % 1000000) * 1000
        }
    };

    itimerspec_dump(&timerspec);

    if (timerfd_settime(fd, 0, &timerspec, NULL) < 0) {
        handle_error("timerfd_settime");
    }

    return fd;
}

void process_command(struct stepperd *stepperd, char *command) {
    printf("processing: %s\n", command);
}

void handle_input(struct stepperd *stepperd) {
    char tmp[BUFFER_MAX];
    struct stepperd_buffer *buffer = &stepperd->input_buffer;
    int ret = read(STDIN_FILENO, &buffer->buf[buffer->pos], BUFFER_MAX - buffer->pos);

    if (ret == 0) {
        printf("stdin ended... exiting\n");
        exit(EXIT_SUCCESS);
    }

    if (ret == -1)
        handle_error("stdin read");

    buffer->pos += ret;
    if (buffer->pos == BUFFER_MAX) {
        fprintf(stderr, "read buffer filled\n");
        buffer->pos = 0;
    }
    buffer->buf[buffer->pos] = 0; // ensure NULL-terminated

    // find the last line
    char *last = strrchr((char *) buffer->buf, '\n');
    if (last == NULL) {
        return;
    }

    // there is a remainder if the '\n' isn't the last char
    char *remainder = NULL;
    *last = 0;
    if ((uint8_t *) last - buffer->buf != buffer->pos - 1)
        remainder = last;
    last = strrchr((char *) buffer->buf, '\n');

    if (last == NULL) {
        last = (char *) buffer->buf - 1;
        buffer->pos = 0;
    }
    

    strcpy(tmp, last + 1);
    if (remainder != NULL) {
        printf("remainder: %s\n", remainder + 1);
        strcpy((char *) buffer->buf, remainder + 1);
        buffer->pos = buffer->pos - (remainder - (char *) buffer->buf) - 1;
    }

    process_command(stepperd, tmp);
}

void event_loop(struct stepperd *stepperd) {
    struct epoll_event events[3];
    uint64_t expirations;

    int ret = 0;
    while (ret != -1) {
        ret = epoll_wait(stepperd->efd, events, sizeof(events), -1);

        for (int i = 0; i < ret; i++) {
            struct epoll_event event = events[i];
            switch (event.data.u32) {
                case POLL_STDIN:
                    handle_input(stepperd);
                    break;
                case POLL_TIMER:
                    if (read(stepperd->tfd, &expirations, sizeof(uint64_t)) == -1)
                        perror("failed to read from timer");

                    if (expirations != 1)
                        fprintf(stderr, "cannot keep up with timer intervals!\n");
                    break;
                default:
                    fprintf(stderr, "Unknown event %d\n", event.data.u32);
            }
        }
    }

    perror("epoll_wait");
}

int main(int argc, char *argv[]) {
    struct stepperd stepperd = {0};
    struct epoll_event ev;

    if (argc != 2) {
        fprintf(stderr, "usage: %s [time]\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    int usec = strtol(argv[1], NULL, 10);

    int tfd = setup_timer(usec);
    int efd = epoll_create1(0);
    if (efd == -1)
        handle_error("epoll_create1");

    stepperd.efd = efd;
    stepperd.tfd = tfd;

    // Setup timer events
    ev.events = EPOLLIN | EPOLLET; // timer events are edge-triggered
    ev.data.u32 = POLL_TIMER;
    epoll_ctl(efd, EPOLL_CTL_ADD, tfd, &ev);

    // Setup stdin events
    fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK);
    ev.events = EPOLLIN;
    ev.data.u32 = POLL_STDIN;
    epoll_ctl(efd, EPOLL_CTL_ADD, STDIN_FILENO, &ev);

    event_loop(&stepperd);

    return 0;
}

void itimerspec_dump(struct itimerspec *ts) {
    printf("itimer: [ interval=%lu s %lu ns, next expire=%lu s %lu ns ]\n",
            ts->it_interval.tv_sec,
            ts->it_interval.tv_nsec,
            ts->it_value.tv_sec,
            ts->it_value.tv_nsec);
}

