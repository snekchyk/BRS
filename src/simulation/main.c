#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define g 9.8
#define dt 0.01
#define pi 3.141592
#define to_radians(deg) ((deg) * pi / 180.0)
#define cd 0.4
#define ro 1.225
#define area 0.1

typedef struct {
    double x, y;
    double vx, vy;
    double v;
    double t;
    double ax;
    double ay;
    
    double angle;
    double dry_mass;
    double thrust;
    double burn_rate;

    double m;
    double fuel;

    //extra telemetry
    double Ep;
    double Ek;
} RocketState;

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif


void update_telemetry(RocketState *rocket);
double calculate_air_density(double y);
int validation(RocketState *rocket);
void calculate_forces(RocketState *rocket, double *Fx, double *Fy, double y0);
void update_velocity(RocketState *rocket, double *Fx, double *Fy);
void update_position(RocketState *rocket);

EXPORT int run_simulation(
    double x0, double y0, double angle, double dry_mass, double thrust, double burn_rate, double fuel,
    double** out_t, double** out_x, double** out_y, double** out_vx, double** out_vy, double** out_ax, double** out_ay, double** out_Ep, double** out_Ek, double** out_m, double** out_fuel
) {
    RocketState rocket;

    rocket.x = x0;
    rocket.y = y0;

    rocket.vx = 0.0;
    rocket.vy = 0.0;
    rocket.t = 0.00;

    angle = to_radians(angle);
    rocket.angle = angle;
    rocket.dry_mass = dry_mass;
    rocket.thrust = thrust;
    rocket.burn_rate = burn_rate;

    double m = dry_mass + fuel;
    rocket.m = m;
    rocket.fuel = fuel;

    rocket.Ep = 0.0;
    rocket.Ek = 0.0;

    if (validation(&rocket) != 0) {
        printf("Simulation aborted due to invalid input.\n");
        return -1;
    }

    int cap = 1000;
    int i = 0;

    *out_t = (double*)malloc(cap * sizeof(double));
    *out_x = (double*)malloc(cap * sizeof(double));
    *out_y = (double*)malloc(cap * sizeof(double));
    *out_vx = (double*)malloc(cap * sizeof(double));
    *out_vy = (double*)malloc(cap * sizeof(double));
    *out_ax = (double*)malloc(cap * sizeof(double));
    *out_ay = (double*)malloc(cap * sizeof(double));
    *out_Ep = (double*)malloc(cap * sizeof(double));
    *out_Ek = (double*)malloc(cap * sizeof(double));
    *out_m = (double*)malloc(cap * sizeof(double));
    *out_fuel = (double*)malloc(cap * sizeof(double));


    while (rocket.y >= 0.0) {
        double x_prev = rocket.x;
        double y_prev = rocket.y;

        if (rocket.fuel > rocket.burn_rate * dt) {
            rocket.fuel -= rocket.burn_rate * dt;
        } else {
            rocket.fuel = 0.0;
        }
        rocket.m = rocket.dry_mass + rocket.fuel;

        double Fx, Fy;
        
        calculate_forces(&rocket, &Fx, &Fy, y0);
        update_velocity(&rocket, &Fx, &Fy);

        update_position(&rocket);

        update_telemetry(&rocket);

        rocket.t += dt;

        if (i >= cap) {
            cap *= 2;
            *out_t = (double*)realloc(*out_t, cap * sizeof(double));
            *out_x = (double*)realloc(*out_x, cap * sizeof(double));
            *out_y = (double*)realloc(*out_y, cap * sizeof(double));
            *out_vx = (double*)realloc(*out_vx, cap * sizeof(double));
            *out_vy = (double*)realloc(*out_vy, cap * sizeof(double));
            *out_ax = (double*)realloc(*out_ax, cap * sizeof(double));
            *out_ay = (double*)realloc(*out_ay, cap * sizeof(double));
            *out_Ep = (double*)realloc(*out_Ep, cap * sizeof(double));
            *out_Ek = (double*)realloc(*out_Ek, cap * sizeof(double));
            *out_m = (double*)realloc(*out_m, cap * sizeof(double));
            *out_fuel = (double*)realloc(*out_fuel, cap * sizeof(double));
        }

        if (rocket.y < 0.0) {
            double fraction = y_prev / (y_prev - rocket.y);
            
            rocket.x = x_prev + fraction * (rocket.x - x_prev);
            rocket.y = 0.0;

            (*out_t)[i] = rocket.t; 
            (*out_x)[i] = rocket.x; 
            (*out_y)[i] = rocket.y;
            (*out_vx)[i] = rocket.vx; 
            (*out_vy)[i] = rocket.vy;
            (*out_ax)[i] = rocket.ax;
            (*out_ay)[i] = rocket.ay;
            (*out_Ep)[i] = rocket.Ep;
            (*out_Ek)[i] = rocket.Ek;
            (*out_m)[i] = rocket.m;
            (*out_fuel)[i] = rocket.fuel;
            i++;
            break;
        }

        if (rocket.fuel <= 0.0 && rocket.y <= 0.001 && rocket.t > 1.0) {
            printf("Simulation stopped: Rocket ran out of fuel on the ground.\n");
            break;
        }

        (*out_t)[i] = rocket.t; (*out_x)[i] = rocket.x; (*out_y)[i] = rocket.y;
        (*out_vx)[i] = rocket.vx; (*out_vy)[i] = rocket.vy;
        (*out_ax)[i] = rocket.ax; (*out_ay)[i] = rocket.ay;
        (*out_Ep)[i] = rocket.Ep; (*out_Ek)[i] = rocket.Ek;
        (*out_m)[i] = rocket.m; (*out_fuel)[i] = rocket.fuel;
        i++;
    }

    return i;
}

int validation(RocketState *rocket) {
    if (rocket->dry_mass <= 0) {
        printf("Error: Rocket dry mass can't be zero or negative.\n");
        return 1;
    }

    if (rocket->thrust < 0) {
        printf("Error: Rocket thrust can't be negative.\n");
        return 1;
    }

    if (rocket->burn_rate < 0) {
        printf("Error: Rocket burn rate can't be negative.\n");
        return 1;
    }

    if (rocket->fuel < 0) {
        printf("Error: Rocket fuel can't be negative.\n");
        return 1;
    }

    if (rocket->thrust <= rocket->dry_mass * g) {
        printf("Warning: Thrust is less than rocket weight. The rocket will never lift off.\n");
        return 0;
    } else if (rocket->thrust <= rocket->m * g) {
        printf("Warning: Thrust is less than initial weight. The rocket will sit on the ground until enough fuel burns off to lift off.\n");
        return 0;
    }

    return 0;

}

double calculate_air_density(double y) {
    if (y < 0) return ro;

    double H = 8500.0;

    return ro * exp(-y / H);
}

void update_telemetry(RocketState *rocket) {
    rocket->Ep = rocket->m * g * rocket->y;



    rocket->Ek = (rocket->m * rocket->v * rocket->v)/2;
}

void calculate_forces(RocketState *rocket, double *Fx, double *Fy, double y0) {
    *Fx = 0.0;
    *Fy = 0.0;

    *Fy = -rocket->m * g;

    if (rocket->fuel > 0.0) {
        *Fx += rocket->thrust * cos(rocket->angle);
        *Fy += rocket->thrust * sin(rocket->angle);
    }

    if (rocket->v > 0.1) {
        double current_ro = calculate_air_density(rocket->y);

        double F_drag = 0.5 * current_ro * cd * area * rocket->v * rocket->v;

        double Fx_drag = -F_drag * (rocket->vx / rocket->v);
        double Fy_drag = -F_drag * (rocket->vy / rocket->v);
        *Fx += Fx_drag;
        *Fy += Fy_drag;
    }

    double N = -(*Fy);
    if (rocket->y <= y0 + 0.001) {
        if (N > 0.0) {
            *Fy += N;
            *Fx = 0.0;
        }
    }

}

void update_velocity(RocketState *rocket, double *Fx, double *Fy) {
    double ax, ay;
    ax = *Fx/rocket->m;
    ay = *Fy/rocket->m;

    rocket->ax = ax;
    rocket->ay = ay;

    rocket->vx += ax*dt;
    rocket->vy += ay*dt;

    rocket->v = sqrt(rocket->vx * rocket->vx + rocket->vy * rocket->vy);
}

void update_position(RocketState *rocket) {
    rocket->x += rocket->vx * dt;
    rocket->y += rocket->vy * dt;
}

EXPORT void free_memory(double* ptr) {
    if (ptr != NULL) {
        free(ptr);
    }
}