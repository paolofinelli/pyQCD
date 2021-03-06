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
 * Created by Matt Spraggs on 06/02/17.
 *
 * Tests for the Wilson fermion action.
 */

#include <fermions/wilson_action.hpp>
#include <utils/matrices.hpp>

#include "helpers.hpp"


TEST_CASE ("Testing Wilson fermion action")
{
  using GaugeLink = pyQCD::ColourMatrix<double, 3>;
  using GaugeField = pyQCD::LatticeColourMatrix<double, 3>;
  using SiteFermion = pyQCD::ColourVector<double, 3>;
  using FermionField = pyQCD::LatticeColourVector<double, 3>;

  const pyQCD::Site shape{8, 4, 4, 4};
  const pyQCD::LexicoLayout layout(shape);

  GaugeField gauge_field(layout, GaugeLink::Identity(), 4);
  FermionField psi(layout, SiteFermion::Ones(), 4);

  const std::vector<double> boundary_phases(4, 0.0);
  
  pyQCD::fermions::WilsonAction<double, 3> wilson_action(0.1, gauge_field,
                                                         boundary_phases);

  auto eta = wilson_action.apply_full(psi);

  const MatrixCompare<SiteFermion> comp(1e-5, 1e-8);

  for (unsigned site = 0; site < layout.volume(); ++site) {
    for (unsigned spin = 0; spin < 4; ++spin) {
      REQUIRE (comp(eta(site, spin), SiteFermion::Ones() * 0.1));
    }
  }

  gauge_field.fill(GaugeLink::Zero());
  psi.fill(SiteFermion::Zero());

  pyQCD::Site site{0, 3, 0, 0};
  pyQCD::RandGenerator rng;
  const auto random_mat = pyQCD::random_sun<double, 3>(rng);
  gauge_field(site, 1) = random_mat;
  psi(site, 3) = SiteFermion::Ones();
  site = {0, 0, 0, 1};
  gauge_field(pyQCD::Site{0, 0, 0, 0}, 3) = random_mat;
  psi(site, 2) = SiteFermion::Ones();
  site = {7, 0, 0, 0};
  gauge_field(site, 0) = random_mat;
  psi(site, 2) = SiteFermion::Ones();

  const SiteFermion expected =
      -0.5 * (pyQCD::I * (random_mat - random_mat.adjoint())  +
          random_mat.adjoint()) * SiteFermion::Ones();

  wilson_action = pyQCD::fermions::WilsonAction<double, 3>(0.0, gauge_field,
                                                           boundary_phases);

  eta = wilson_action.apply_full(psi);

  REQUIRE (comp(eta[0], expected));
}