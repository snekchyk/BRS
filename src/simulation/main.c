#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define g 9.8
#define pi 3.141592
#define to_radians(deg) ((deg) * pi / 180.0)

double get_Sx(double v0x, double t);
double get_Sy(double v0y, double t);

int main() {

    double v0, angle, x0, y0;

    printf("Enter initial velocity: ");
    if(scanf("%lf", &v0) != 1) {
        printf("Error reading data.\n");
        return 1;
    }


    printf("Enter angle: ");
    if(scanf("%lf", &angle) != 1) {
        printf("Error reading data.\n");
        return 1;
    }
    angle = to_radians(angle);

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

    FILE *file = fopen("trajectory.txt", "w");
    if (file == NULL) {
        perror("Error opening file");
        return 1;
    }
    double v0x = v0 * cos(angle);
    double v0y = v0 * sin(angle);
    double full_t = (v0y + sqrt(v0y * v0y + 2 * g * y0))/g;
    double t = 0.0;

    while (t <= full_t) {
        double Sx = get_Sx(v0x, t);
        double Sy = get_Sy(v0y, t);

        fprintf(file, "%lf;%lf;%lf;%lf;%lf\n", t, Sx, Sy, x0 + Sx, y0 + Sy);
        t += 0.01;
    }
    double Sx = v0x * full_t;
    double Sy = v0y * full_t - g*pow(full_t, 2)/2;
    fprintf(file, "%lf;%lf;%lf;%lf;%lf\n", full_t, Sx, Sy, x0 + Sx, y0 + Sy);

    fclose(file);
    printf("Data successfully written to trajectory.txt\n");
}

double get_Sx(double v0x, double t) {
    return (v0x * t);
}

double get_Sy(double v0y, double t) {
    return (v0y * t - (g*pow(t, 2))/2);
}
