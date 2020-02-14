#include "event.h"

#include "util.h"

#include <error.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/timerfd.h>
#include <unistd.h>

#define POLL_STDIN 0
#define POLL_STDOUT 1
#define POLL_TIMER 2

static int handle_input(struct rio_buffer *buffer, char *command, size_t size) {
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
        return 0;
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
    

    size_t length = strlen(last + 1);
    if (length >= size)
        return -1;

    strcpy(command, last + 1);
    if (remainder != NULL) {
        strcpy((char *) buffer->buf, remainder + 1);
        buffer->pos = buffer->pos - (remainder - (char *) buffer->buf) - 1;
    }

    return length;
}

void rio_init(struct rio *rio) {
    struct epoll_event ev;

    rio->efd = epoll_create1(0);
    if (rio->efd == -1)
        handle_error("epoll_create1");

    rio->input_buffer.pos = 0;
    rio->output_buffer.pos = 0;

    rio->tfd = timerfd_create(CLOCK_REALTIME, TFD_NONBLOCK);
    fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK);

    // Setup timer events
    ev.events = EPOLLIN | EPOLLET; // timer events are edge-triggered
    ev.data.u32 = POLL_TIMER;
    epoll_ctl(rio->efd, EPOLL_CTL_ADD, rio->tfd, &ev);

    // Setup stdin events
    fcntl(STDIN_FILENO, F_SETFL, O_NONBLOCK);
    ev.events = EPOLLIN;
    ev.data.u32 = POLL_STDIN;
    epoll_ctl(rio->efd, EPOLL_CTL_ADD, STDIN_FILENO, &ev);

    // TODO: Handle STDOUT
}


void rio_finish(struct rio *rio) {
    // TODO: close epoll stuff
}

void rio_run(struct rio *rio, struct rio_cb callback, void *data) {
    struct epoll_event events[3];
    char command[BUFFER_MAX];
    int len;

    int ret = 0;
    while (ret != -1) {
        ret = epoll_wait(rio->efd, events, sizeof(events), -1);

        for (int i = 0; i < ret; i++) {
            struct epoll_event event = events[i];
            switch (event.data.u32) {
                case POLL_STDIN:
                    len = handle_input(&rio->input_buffer, command, BUFFER_MAX);
                    if (len == 0)
                        continue;

                    callback.command_cb(data, command);
                    break;
                case POLL_TIMER:
                    callback.timer_cb(data, rio->tfd);
                    break;
                default:
                    fprintf(stderr, "Unknown event %d\n", event.data.u32);
            }
        }
    }

    perror("epoll_wait");
}

