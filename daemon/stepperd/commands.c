#include "stepperd/commands.h"
#include "stepperd/stepperd.h"

#include <stdio.h>
#include <string.h>

// configure <step_time> <step_angle1> <step_angle2>
int cmd_configure(void *data, char *arg_line) {
    struct stepperd *stepperd = data;
    char *error;
    char *tmp;

    printf("configure: %s\n", arg_line);
   
    tmp = strtok(arg_line, " ");
    if (tmp == NULL) {
        return -1;
    }
    stepperd->step_time = strtol(tmp, &error, 10);
    if (*error != '\0') {
        return -1;
    }

    tmp = strtok(NULL, " ");
    if (tmp == NULL) {
        return -1;
    }
    stepperd->motors[0].step_angle = strtod(tmp, &error);
    if (*error != '\0') {
        return -1;
    }

    tmp = strtok(NULL, " ");
    if (tmp == NULL) {
        return -1;
    }
    stepperd->motors[1].step_angle = strtod(tmp, &error);
    if (*error != '\0') {
        return -1;
    }

    return 0;
}

int cmd_set(void *data, char *arg_line) {
    struct stepperd *stepperd = data;
    printf("set: %s\n", arg_line);
    return 0;
}

static struct cmd_handler handlers[] = {
    { "configure", cmd_configure },
    { "set", cmd_set },
};

void stepperd_commands_init(struct commands *commands) {
    commands->commands = handlers;
    commands->len = sizeof(handlers) / sizeof(struct cmd_handler);
}

