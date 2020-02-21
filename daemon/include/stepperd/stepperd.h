#ifndef STEPPERD_STEPPERD_H
#define STEPPERD_STEPPERD_H

#include "commands.h"
#include "event.h"

#include <stdbool.h>
#include <time.h>

struct stepperd_target {
    bool is_valid;
    uint32_t target_steps;
};

struct stepperd_motor {
    double step_angle; // radians per step
    uint32_t cur_step; // current steps

    struct stepperd_target target;
};

struct stepperd {
    struct rio rio;
    struct commands commands;

    uint32_t step_time; // T_high, T_low in ns
    struct stepperd_motor motors[2];
};

#endif

