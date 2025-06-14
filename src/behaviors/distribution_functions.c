/*@author cdimidov*/

#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "distribution_functions.h"

double uniform_distribution(double a, double b)
{

  return (rand() * (b - a) + a) / ((double)RAND_MAX + 1);
}
// oppure
/*
double uniform_distribution()
{
  return rand()/(double)(RAND_MAX+1.0);
  

}*/

double wrapped_cauchy_ppf(const double c)
{
  double val, theta, u, q;
  q = 0.5;
  u = uniform_distribution(0.0, 1.0);
  val = (1.0 - c) / (1.0 + c);
  theta = 2 * atan(val * tan(M_PI * (u - q)));
  return theta;
}

/*double exponential_distribution (double lambda, double a, double b)
{
  double u,x;
  u = uniform_distribution(a,b);
  x=(-1/lambda)*log(u);
  return(x);
}*/

double exponential_distribution(double lambda)
{
  double u, x;
  u = uniform_distribution(0.0, 1.0);
  x = (-lambda) * log(1 - u);
  return (x);
}

/* The stable Levy probability distributions have the form

   p(x) dx = (1/(2 pi)) \int dt exp(- it x - |c t|^alpha)

   with 0 < alpha <= 2. 

   For alpha = 1, we get the Cauchy distribution
   For alpha = 2, we get the Gaussian distribution with sigma = sqrt(2) c.

   */

int levy(const double c, const double alpha)
{
  double u, v, t, s;

  u = M_PI * (uniform_distribution(0.0, 1.0) - 0.5); /*vedi uniform distribution */

  if (alpha == 1) /* cauchy case */
  {
    t = tan(u);
    return (int)(c * t);
  }

  do
  {
    v = exponential_distribution(1.0); /*vedi esponential distribution */
  } while (v == 0);

  if (alpha == 2) /* gaussian case */
  {
    t = 2 * sin(u) * sqrt(v);
    return (int)(c * t);
  }

  /* general case */

  t = sin(alpha * u) / pow(cos(u), 1 / alpha);
  s = pow(cos((1 - alpha) * u) / v, (1 - alpha) / alpha);

  return (int)(c * t * s);
}
