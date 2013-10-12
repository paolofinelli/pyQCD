#include <pylattice.hpp>

pyLattice::pyLattice(const int spatialExtent,
		     const int temporalExtent,
		     const double beta,
		     const double u0,
		     const int action,
		     const int nCorrelations,
		     const int updateMethod,
		     const int parallelFlag,
		     const int chunkSize,
		     const int randSeed) :
  Lattice::Lattice(spatialExtent, temporalExtent, beta, u0, action,
		   nCorrelations, updateMethod, parallelFlag, chunkSize,
		   randSeed)
{
  
}



pyLattice::pyLattice(const pyLattice& pylattice) : 
  Lattice::Lattice(pylattice)
{
  
}



pyLattice::~pyLattice()
{
  
}



double pyLattice::computePlaquetteP(const py::list site2, const int mu,
				    const int nu)
{
  // Python wrapper for the plaquette function.
  int site[4] = {py::extract<int>(site2[0]),
		 py::extract<int>(site2[1]),
		 py::extract<int>(site2[2]),
		 py::extract<int>(site2[3])};
  return this->computePlaquette(site, mu, nu);
}



double pyLattice::computeRectangleP(const py::list site, const int mu,
				    const int nu)
{
  // Python wrapper for rectangle function.
  int tempSite[4] = {py::extract<int>(site[0]),
		     py::extract<int>(site[1]),
		     py::extract<int>(site[2]),
		     py::extract<int>(site[3])};
  return this->computeRectangle(tempSite, mu, nu);
}



double pyLattice::computeTwistedRectangleP(const py::list site,
					   const int mu, const int nu)
{
  // Python wrapper for rectangle function
  int tempSite[4] = {py::extract<int>(site[0]),
		     py::extract<int>(site[1]),
		     py::extract<int>(site[2]),
		     py::extract<int>(site[3])};
  return this->computeTwistedRectangle(tempSite, mu, nu);
}



double pyLattice::computeWilsonLoopP(const py::list corner, const int r,
				     const int t, const int dimension,
				     const int nSmears,
				     const double smearingParameter)
{
  // Calculates the loop specified by corners c1 and c2 (which must
  // lie in the same plane)
  int tempCorner[4] = {py::extract<int>(corner[0]),
		       py::extract<int>(corner[1]),
		       py::extract<int>(corner[2]),
		       py::extract<int>(corner[3])};

  return this->computeWilsonLoop(tempCorner, r, t, dimension, nSmears,
				 smearingParameter);
}



double pyLattice::computeAverageWilsonLoopP(const int r, const int t,
					    const int nSmears,
					    const double smearingParameter)
{
  // Wrapper for the expectation value for the Wilson loop
  ScopedGILRelease scope;
  return this->computeAverageWilsonLoop(r, t, nSmears, smearingParameter);
}



py::list pyLattice::computePropagatorP(const double mass, const double spacing,
				       const py::list site, const int nSmears,
				       const double smearingParameter,
				       const int nSourceSmears,
				       const double sourceSmearingParameter,
				       const int nSinkSmears,
				       const double sinkSmearingParameter,
				       const int solverMethod,
				       const int verbosity)
{
  // Wrapper for the calculation of a propagator
  int tempSite[4] = {py::extract<int>(site[0]),
		     py::extract<int>(site[1]),
		     py::extract<int>(site[2]),
		     py::extract<int>(site[3])};
  // Release the GIL for the propagator inversion (not necessary but here anyway)
  ScopedGILRelease* scope = new ScopedGILRelease;
  // Get the propagator
  vector<MatrixXcd> prop = this->computePropagator(mass, spacing, tempSite,
						   nSmears,
						   smearingParameter,
						   nSourceSmears,
						   sourceSmearingParameter,
						   nSinkSmears,
						   sinkSmearingParameter,
						   solverMethod,
						   verbosity);
  // Put GIL back in place
  delete scope;
  // This is where we'll store the propagator as a list
  py::list pythonPropagator;
  // Loop through the raw propagator and add it to the python list
  for (int i = 0; i < this->nLinks_ / 4; ++i) {
    // Maybe the following could be put in it's own function? Seems to be
    // something that frequently needs to be done
    py::list matrixList = pyQCD::convertMatrixToList(prop[i]);
    pythonPropagator.append(matrixList);
  }

  return pythonPropagator;
}



void pyLattice::runThreads(const int nUpdates, const int remainder)
{
  // Need to overload this and release the GIL
  ScopedGILRelease scope;
  Lattice::runThreads(nUpdates, remainder);
}



py::list pyLattice::getLinkP(const py::list link)
{
  // Returns the given link as a python nested list. Used in conjunction
  // with python interfaces library to extract the links as a nested list
  // of numpy matrices.
  int tempLink[5] = {py::extract<int>(link[0]),
		     py::extract<int>(link[1]),
		     py::extract<int>(link[2]),
		     py::extract<int>(link[3]),
		     py::extract<int>(link[4])};
  // Convert the Matrix3cd to a python list
  return pyQCD::convertMatrixToList(this->getLink(tempLink));
}



void pyLattice::setLinkP(const py::list link, const py::list matrix)
{
  // Set the given link to the values specified in matrix
  int tempLink[5] = {py::extract<int>(link[0]),
		     py::extract<int>(link[1]),
		     py::extract<int>(link[2]),
		     py::extract<int>(link[3]),
		     py::extract<int>(link[4])};
  Matrix3cd tempMatrix = pyQCD::convertListToMatrix(matrix);
  this->setLink(tempLink, tempMatrix);
}



py::list pyLattice::getRandSu3(const int index) const
{
  // Returns the given random SU3 matrix as a python list
  return pyQCD::convertMatrixToList(this->randSu3s_[index]);
}
