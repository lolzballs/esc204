#include "util.h"
#include "stepperd/stepperd.h"
#include "stepperd/commands.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/timerfd.h>
#include <time.h>
#include <unistd.h>

#define GPIOCHIP_NUM 0
#define MOTOR1_STEP 27
#define MOTOR1_DIR 22
#define MOTOR2_STEP 23
#define MOTOR2_DIR 24

static void setup_timer(int tfd, int usec) {
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

static void process_command(void *data, char *line) {
    struct stepperd *stepperd = data;
    int ret = command_exec(&stepperd->commands, line);
    if (ret != 0)
        fprintf(stderr, "bad command\n");
}

static void process_timer(void *data, int tfd) {
    struct stepperd *stepperd = data;
    uint64_t expirations;
    bool done = true;

    read(tfd, &expirations, sizeof(expirations));
    if (expirations != 1)
        fprintf(stderr, "cannot keep up with timer intervals!\n");

    size_t num_motors = sizeof(stepperd->motors) / sizeof(struct stepperd_motor);
    for (size_t i = 0; i < num_motors; i++) {
        struct stepperd_motor motor = stepperd->motors[i];

        int step_state = gpiod_line_get_value(motor.step_pin);
        assert(step_state != -1);

        // when the step pin is high, we are in the middle of a step 
        if (step_state) {
            assert(gpiod_line_set_value(motor.step_pin, !step_state) != -1);
            continue;
        }

        if (!motor.target.is_valid) {
            continue;
        }

        // ensure we are going in the correct direction
        int dir_state = gpiod_line_get_value(motor.dir_pin);
        assert(dir_state != -1);
        if (motor.target.clockwise != dir_state)
            assert(gpiod_line_set_value(motor.dir_pin, !dir_state) != -1);

        // update motor state
        if (motor.cur_step == 0 && !dir_state)
            motor.cur_step = motor.steps_per_rot - 1;
        else if (motor.cur_step  == motor.steps_per_rot - 1 && dir_state)
            motor.cur_step = 0;
        else
            motor.cur_step += dir_state ? 1 : -1;

        motor.target.steps_elapsed++;
        motor.target.is_valid = motor.target.steps_elapsed != motor.target.step_count;
        if (!motor.target.is_valid)
            done = false;

        // actually step
        assert(gpiod_line_set_value(motor.step_pin, !step_state) != -1);
    }

    if (done && stepperd->pending) {
        rio_write_string(&stepperd->rio, "set done\n");
        stepperd->pending = false;
    }
}

static int init_motor(struct stepperd_motor *motor, struct gpiod_chip *chip,
    unsigned int step_pin, unsigned int dir_pin) {
    motor->step_pin = gpiod_chip_get_line(chip, step_pin);
    assert(motor->step_pin != NULL);
    assert(gpiod_line_request_output(motor->step_pin, "stepperd", 0) == 0);

    motor->dir_pin = gpiod_chip_get_line(chip, dir_pin);
    assert(motor->dir_pin != NULL);
    assert(gpiod_line_request_output(motor->dir_pin, "stepperd", 0) == 0);

    motor->cur_step = 0;
    motor->target.is_valid = false;
    return 0;
}

int main(int argc, char *argv[]) {
    struct rio rio;
    if (argc != 2) {
        fprintf(stderr, "usage: %s [time]\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    struct gpiod_chip *chip = gpiod_chip_open_by_number(0);
    if (chip == NULL) {
        fprintf(stderr, "failed to open gpio chip\n");
        exit(EXIT_FAILURE);
    }

    struct commands commands;
    commands.data = &rio;
    stepperd_commands_init(&commands);

    struct stepperd stepperd = {
        .rio = rio,
        .commands = commands,
        .pending = false,
        .chip = chip,
    };

    assert(init_motor(&stepperd.motors[0], chip, MOTOR1_STEP, MOTOR1_DIR) == 0);
    assert(init_motor(&stepperd.motors[1], chip, MOTOR2_STEP, MOTOR2_DIR) == 0);

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

