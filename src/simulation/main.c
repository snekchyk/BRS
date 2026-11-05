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

void update_telemetry(RocketState *rocket);
int validation(RocketState *rocket);
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

    rocket.Ep = 0.0;
    rocket.Ek = 0.0;

    if (validation(&rocket) != 0) {
        printf("Simulation aborted due to invalid input.\n");
        return 1;
    }

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

        update_telemetry(&rocket);

        update_position(&rocket);

        if (rocket.fuel > 0.0) {
            rocket.fuel -= rocket.burn_rate * dt;
            if (rocket.fuel < 0.0) rocket.fuel = 0.0;
            rocket.m = rocket.dry_mass + rocket.fuel;
        }

        rocket.t += dt;

        if (rocket.y < 0.0) {
            double fraction = y_prev / (y_prev - rocket.y);
            
            rocket.x = x_prev + fraction * (rocket.x - x_prev);
            rocket.y = 0.0;
            
            fprintf(file, "%lf;%lf;%lf;%lf;%lf;%lf;%lf;%lf;%lf%;lf;%lf\n", rocket.t, rocket.x, rocket.y, rocket.vx, rocket.vy, rocket.ax, rocket.ay, rocket.Ep, rocket.Ek, rocket.m, rocket.fuel);
            break;
        }

        fprintf(file, "%lf;%lf;%lf;%lf;%lf;%lf;%lf;%lf;%lf;%lf;%lf\n", rocket.t, rocket.x, rocket.y, rocket.vx, rocket.vy, rocket.ax, rocket.ay, rocket.Ep, rocket.Ek, rocket.m, rocket.fuel);
    }


    fclose(file);
    printf("Data successfully written to trajectory.txt\n");
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