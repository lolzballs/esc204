#include "stepperd/commands.h"
#include "stepperd/stepperd.h"

#include <stdio.h>
#include <string.h>
#include <sys/timerfd.h>

static int setup_timer(int tfd, int usec) {
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
        fprintf(stderr, "timerfd_settime failed\n");
	return -1;
    }

    return 0;
}

// returns true it is already there
static bool normalize_steps(struct stepperd_motor *motor, int32_t target_steps) {
    uint32_t full_rot = motor->steps_per_rot;
    uint32_t cur_step = motor->cur_step;

    while (target_steps < 0) {
        target_steps = full_rot + target_steps; // make it a positive angle
    }
    target_steps = target_steps % full_rot; // normalize to [0, full_rot]

    // determine direction
    int32_t cw_steps = target_steps - cur_step;
    int32_t ccw_steps = full_rot - cw_steps;
    if (cw_steps < 0) {
        ccw_steps = -cw_steps;
        cw_steps = full_rot - ccw_steps;
    }

    if (cw_steps == 0)
        return true;

    motor->target.is_valid = true;
    motor->target.step_count = 0;
    motor->target.steps_elapsed = 0;
    if (cw_steps > ccw_steps) {
        motor->target.clockwise = false;
        motor->target.step_count = ccw_steps;
    } else {
        motor->target.clockwise = true;
        motor->target.step_count = cw_steps;
    }

    return false;
}

// configure <step_time> <step_angle1> <step_angle2>
int cmd_configure(void *data, char *arg_line) {
    struct stepperd *stepperd = data;
    char *error;
    char *tmp;

    tmp = strtok(arg_line, " ");
    if (tmp == NULL)
        return -1;

    stepperd->step_time = strtol(tmp, &error, 10);
    if (*error != '\0')
        return -1;

    tmp = strtok(NULL, " ");
    if (tmp == NULL)
        return -1;

    stepperd->motors[0].steps_per_rot = strtol(tmp, &error, 10);
    if (*error != '\0')
        return -1;

    tmp = strtok(NULL, " ");
    if (tmp == NULL)
        return -1;

    stepperd->motors[1].steps_per_rot = strtol(tmp, &error, 10);
    if (*error != '\0')
        return -1;

    if (setup_timer(stepperd->rio.tfd, stepperd->step_time) != 0)
        return -1;

    rio_write_string(&stepperd->rio, "configure done\n");
    return 0;
}

// set <step_angle1> <step_angle2>
int cmd_set(void *data, char *arg_line) {
    struct stepperd *stepperd = data;
    char *error;
    char *tmp;

    stepperd->pending = true;
    
    tmp = strtok(arg_line, " ");
    if (tmp == NULL)
        return -1;

    int32_t step_angle1 = strtol(tmp, &error, 10);
    if (*error != '\0')
        return -1;

    tmp = strtok(NULL, " ");
    if (tmp == NULL)
        return -1;

    int32_t step_angle2 = strtol(tmp, &error, 10);
    if (*error != '\0')
        return -1;

    bool ret1 = normalize_steps(&stepperd->motors[0], step_angle1);
    bool ret2 = normalize_steps(&stepperd->motors[1], step_angle2);

    if (ret1 && ret2) { // both motors are at its target
        stepperd->pending = false;
        rio_write_string(&stepperd->rio, "set done\n");
    }

    return 0;
}

static struct cmd_handler handlers[] = {
    { "configure", cmd_configure },
    { "set", cmd_set },
};

void stepperd_commands_init(struct commands *commands, void *data) {
    commands->data = data;
    commands->commands = handlers;
    commands->len = sizeof(handlers) / sizeof(struct cmd_handler);
}

