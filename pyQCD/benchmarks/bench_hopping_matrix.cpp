/*
 * This file is part of pyQCD.
 *
 * pyQCD is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * pyQCD is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>. *
 *
 * Created by Matt Spraggs on 09/02/17.
 *
 * Benchmark for HoppingMatrix::apply_full function.
 */

#include <fermions/hopping_matrix.hpp>

#include "helpers.hpp"


int main()
{
  const pyQCD::LexicoLayout layout({8, 8, 8, 8});
  const pyQCD::LatticeColourMatrix<double, 3> gauge_field(
      layout, pyQCD::ColourMatrix<double, 3>::Identity(), 4);

  const std::vector<pyQCD::SpinMatrix<double>>
      spin_structures(8, pyQCD::SpinMatrix<double>::Identity(4, 4));
  const std::vector<std::complex<double>> phases(4, 1.0);

  const pyQCD::fermions::HoppingMatrix<double, 3, 1>
      hopping_matrix(gauge_field, phases, spin_structures);

  const pyQCD::LatticeColourVector<double, 3> fermion_in(layout, 4);
  pyQCD::LatticeColourVector<double, 3> fermion_out(layout, 4);

  std::cout << "Benchmarking HoppingMatrix::apply_full..." << std::endl;
  benchmark([&] () {
    fermion_out = hopping_matrix.apply_full(fermion_in);
  }, 0, 100);
}