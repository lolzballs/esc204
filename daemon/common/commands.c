#include "commands.h"

#include <string.h>

int command_exec(struct commands *handler, char *line) {
    char *arg_line = strchr(line, ' ');
    if (arg_line == NULL) {
        return -1;
    }

    *arg_line = '\0';
    arg_line += 1;

    for (size_t i = 0; i < handler->len; i++) {
        struct cmd_handler cmd_handler = handler->commands[i];
        if (strcmp(cmd_handler.command, line) == 0) {
            return cmd_handler.handle(handler->data, arg_line);
        }
    }

    return -1;
}

