#include "stepperd/commands.h"

#include <stdio.h>

int cmd_configure(void *data, char *arg_line) {
    printf("configure: %s\n", arg_line);
    return 0;
}

static struct cmd_handler handlers[] = {
    { "configure", cmd_configure },
};

void stepperd_commands_init(struct commands *commands) {
    commands->commands = handlers;
    commands->len = sizeof(handlers);
}

