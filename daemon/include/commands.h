#ifndef COMMANDS_H
#define COMMANDS_H

#include <stdlib.h>

typedef int cmd_handle(void *data, char *arg_line);

struct cmd_handler {
    char *command;
    cmd_handle *handle;
};

struct commands {
    void *data;

    struct cmd_handler *commands;
    size_t len;
};

int command_exec(struct commands *handler, char *line);

#endif

