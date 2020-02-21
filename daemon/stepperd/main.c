#include "util.h"
#include "stepperd/stepperd.h"
#include "stepperd/commands.h"

#include <stdio.h>
#include <string.h>
#include <sys/timerfd.h>
#include <time.h>
#include <unistd.h>

void setup_timer(int tfd, int usec) {
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

    if (timerfd_settime(tfd, 0, &timerspec, NULL) < 0) {
        handle_error("timerfd_settime");
    }
}

void process_command(void *data, char *line) {
    struct stepperd *stepperd = data;
    int ret = command_exec(&stepperd->commands, line);
    if (ret != 0)
        fprintf(stderr, "bad command\n");
}

void process_timer(void *data, int tfd) {
    uint64_t expirations;
    read(tfd, &expirations, sizeof(expirations));

    if (expirations != 1)
        fprintf(stderr, "cannot keep up with timer intervals!\n");
}

int main(int argc, char *argv[]) {
    struct rio rio;
    if (argc != 2) {
        fprintf(stderr, "usage: %s [time]\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    struct commands commands;
    commands.data = &rio;
    stepperd_commands_init(&commands);

    struct stepperd stepperd = {
        .commands = commands,
        .rio = rio
    };

    struct rio_cb rio_cb = {
        .command_cb = process_command,
        .timer_cb = process_timer,
    };

    int usec = strtol(argv[1], NULL, 10);

    rio_init(&rio);

    setup_timer(rio.tfd, usec);

    rio_run(&rio, rio_cb, &stepperd);
    rio_finish(&rio);

    return 0;
}

