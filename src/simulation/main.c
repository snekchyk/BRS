#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define g 9.8
#define dt 0.01
#define pi 3.141592
#define to_radians(deg) ((deg) * pi / 180.0)

typedef struct {
    double x, y;
    double vx, vy;
    double t;

    double angle;
    double dry_mass;
    double thrust;
    double burn_rate;

    double m;
    double fuel;
} RocketState;

void calculate_forces(RocketState *rocket, double *Fx, double *Fy, double y0);
void update_velocity(RocketState *rocket, double *Fx, double *Fy);
void update_position(RocketState *rocket);

int main() {
        double x0, y0, vx, vy, angle, dry_mass, thrust, burn_rate, m, fuel, t;

    printf("Enter 'x' initial position: ");
    if(scanf("%lf", &x0) != 1) {
        printf("Error reading data.\n");
        return 1;
    }

    printf("Enter 'y' initial position: ");
    if(scanf("%lf", &y0) != 1) {
        printf("Error reading data.\n");
        return 1;
    }

    printf("Enter angle: ");
    if(scanf("%lf", &angle) != 1) {
        printf("Error reading data.\n");
        return 1;
    }
    angle = to_radians(angle);

    printf("Enter dry mass: ");
    if(scanf("%lf", &dry_mass) != 1) {
        printf("Error reading data.\n");
        return 1;
    }

    printf("Enter thrust: ");
    if(scanf("%lf", &thrust) != 1) {
        printf("Error reading data.\n");
        return 1;
    }

    printf("Enter burn rate: ");
    if(scanf("%lf", &burn_rate) != 1) {
        printf("Error reading data.\n");
        return 1;
    }

    printf("Enter fuel: ");
    if(scanf("%lf", &fuel) != 1) {
        printf("Error reading data.\n");
        return 1;
    }


    RocketState rocket;


    rocket.x = x0;
    rocket.y = y0;

    rocket.vx = 0.0;
    rocket.vy = 0.0;
    rocket.t = 0.00;


    rocket.angle = angle;
    rocket.dry_mass = dry_mass;
    rocket.thrust = thrust;
    rocket.burn_rate = burn_rate;

    m = dry_mass + fuel;
    rocket.m = m;
    rocket.fuel = fuel;

    FILE *file = fopen("trajectory.txt", "w");
    if (file == NULL) {
        perror("Error opening file");
        return 1;
    }

    while (rocket.y >= 0.0) {
        double x_prev = rocket.x;
        double y_prev = rocket.y;

        double Fx, Fy;

        calculate_forces(&rocket, &Fx, &Fy, y0);

        update_velocity(&rocket, &Fx, &Fy);

        update_position(&rocket);

        if (rocket.fuel > 0.0) {
            rocket.fuel -= rocket.burn_rate * dt;
            if (rocket.fuel < 0.0) rocket.fuel = 0.0;
            rocket.m = rocket.dry_mass + rocket.fuel;
        }

        rocket.t += dt;

        fprintf(file, "%lf;None;None;%lf;%lf\n", rocket.t, rocket.x, rocket.y);
    }


    fclose(file);
    printf("Data successfully written to trajectory.txt\n");
}

void calculate_forces(RocketState *rocket, double *Fx, double *Fy, double y0) {
    *Fx = 0.0;
    *Fy = 0.0;

    *Fy = -rocket->m * g;

    if (rocket->fuel > 0.0) {
        *Fx += rocket->thrust * cos(rocket->angle);
        *Fy += rocket->thrust * sin(rocket->angle);
    }

}

void update_velocity(RocketState *rocket, double *Fx, double *Fy) {
    double ax, ay;
    ax = *Fx/rocket->m;
    ay = *Fy/rocket->m;

    rocket->vx += ax*dt;
    rocket->vy += ay*dt;
}

void update_position(RocketState *rocket) {
    rocket->x += rocket->vx * dt;
    rocket->y += rocket->vy * dt;
}