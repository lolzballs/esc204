#ifndef ROBOT_EVENT_H
#define ROBOT_EVENT_H

#include <stdint.h>
#include <stdlib.h>

#define BUFFER_MAX 1024

typedef void (*rio_command_cb_t)(void *data, char *line);
typedef void (*rio_timer_cb_t)(void *data, int tfd);

struct rio_cb {
    rio_command_cb_t command_cb;
    rio_timer_cb_t timer_cb;
};

struct rio_buffer {
    uint8_t buf[BUFFER_MAX];
    size_t pos;
};

struct rio {
    struct rio_buffer input_buffer;
    struct rio_buffer output_buffer;

    int efd, tfd; // epoll and timerfd
};

void rio_init(struct rio *rio);
void rio_finish(struct rio *rio);

void rio_run(struct rio *rio, struct rio_cb callback, void *data);
int rio_write(struct rio *rio, uint8_t *buf, size_t len);
int rio_write_string(struct rio *rio, char *str);

#endif

