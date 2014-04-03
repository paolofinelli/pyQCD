#ifndef UNPRECONDITIONED_WILSON_HPP
#define UNPRECONDITIONED_WILSON_HPP

#include <Eigen/Dense>

#include <complex>

#include <omp.h>

#include <lattice.hpp>
#include <utils.hpp>
#include <linear_operators/linear_operator.hpp>
#include <linear_operators/wilson_hopping_term.hpp>

using namespace Eigen;
using namespace std;

class UnpreconditionedWilson : public LinearOperator
{
  // Basic unpreconditioned Wilson Dirac operator

public:
  UnpreconditionedWilson(const double mass,
			 const vector<complex<double> >& boundaryConditions,
			 Lattice* lattice);
  ~UnpreconditionedWilson();

  VectorXcd multiplyGamma5(const VectorXcd& psi);

  VectorXcd apply(const VectorXcd& psi);
  VectorXcd applyHermitian(const VectorXcd& psi);
  VectorXcd makeHermitian(const VectorXcd& psi);

private:
  // Pointer to the lattice object containing the gauge links
  Lattice* lattice_;
  WilsonHoppingTerm* hoppingMatrix_; // This operator does the derivative
  double mass_; // Mass of the Wilson fermion
  int operatorSize_; // Size of vectors on which the operator may operate
  // The 1 +/- gamma_mu matrices required by the operator
  vector<Matrix4cd, aligned_allocator<Matrix4cd> > spinStructures_;
  // Nearest neighbour indices
  vector<vector<int> > nearestNeighbours_;
  vector<vector<complex<double> > > boundaryConditions_;
  double tadpoleCoefficients_[4];
};

#endif
