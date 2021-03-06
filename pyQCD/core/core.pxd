"""
Do NOT edit this file. It was generated automatically from a template.

Please edit the files within the template directory of the pyQCD package tree
and run "python setup.py codegen" in the root of the source tree.
"""

from cpython cimport Py_buffer

from libcpp cimport bool as bool_t
from libcpp.vector cimport vector

from atomics cimport Real, Complex
from pyQCD.utils.utils cimport _RandGenerator

cdef extern from "core/layout.hpp" namespace "pyQCD":
    cdef cppclass _Layout "pyQCD::Layout":
        _Layout(const vector[unsigned int]&) except+
        unsigned int get_array_index(const unsigned int)
        unsigned int get_array_index(const vector[unsigned int]&)
        unsigned int get_site_index(const unsigned int)
        unsigned int num_dims()
        unsigned int volume()
        const vector[unsigned int]& shape()

    cdef cppclass _LexicoLayout "pyQCD::LexicoLayout"(_Layout):
        _LexicoLayout(const vector[unsigned int]&) except+

    cdef cppclass _EvenOddLayout "pyQCD::EvenOddLayout"(_Layout):
        _EvenOddLayout(const vector[unsigned int]&) except+


cdef class Layout:
    cdef _Layout* instance


cdef class LexicoLayout(Layout):
    pass


cdef class EvenOddLayout(Layout):
    pass



cdef extern from "core/qcd_types.hpp" namespace "pyQCD":
    cdef cppclass _ColourMatrix "pyQCD::ColourMatrix<pyQCD::Real, pyQCD::num_colours>":
        _ColourMatrix() except +
        _ColourMatrix(const _ColourMatrix&) except +
        _ColourMatrix adjoint()
        Complex& operator()(int, int) except +


    cdef _ColourMatrix _ColourMatrix_zeros "pyQCD::ColourMatrix<pyQCD::Real, pyQCD::num_colours>::Zero"()
    cdef _ColourMatrix _ColourMatrix_ones "pyQCD::ColourMatrix<pyQCD::Real, pyQCD::num_colours>::Ones"()

cdef extern from "utils/matrices.hpp" namespace "pyQCD":
    cdef _ColourMatrix _random_colour_matrix "pyQCD::random_sun<pyQCD::Real, pyQCD::num_colours>"(_RandGenerator& rng)

cdef class ColourMatrix:
    cdef _ColourMatrix* instance
    cdef int view_count
    cdef Py_ssize_t buffer_shape[2]
    cdef Py_ssize_t buffer_strides[2]

cdef extern from "core/qcd_types.hpp" namespace "pyQCD":
    cdef cppclass _LatticeColourMatrix "pyQCD::LatticeColourMatrix<pyQCD::Real, pyQCD::num_colours>":
        _LatticeColourMatrix() except +
        _LatticeColourMatrix(const _Layout&, const _ColourMatrix&, unsigned int site_size) except +
        _ColourMatrix& operator[](const unsigned int)
        unsigned int volume()
        unsigned int num_dims()
        const vector[unsigned int]& lattice_shape()
        void change_layout(const _Layout&) except +

cdef class LatticeColourMatrix:
    cdef _LatticeColourMatrix* instance
    cdef public Layout layout
    cdef bool_t is_buffer_compatible
    cdef int view_count
    cdef public int site_size
    cdef Py_ssize_t buffer_shape[3]
    cdef Py_ssize_t buffer_strides[3]

cdef extern from "core/qcd_types.hpp" namespace "pyQCD":
    cdef cppclass _ColourVector "pyQCD::ColourVector<pyQCD::Real, pyQCD::num_colours>":
        _ColourVector() except +
        _ColourVector(const _ColourVector&) except +
        _ColourVector adjoint()
        Complex& operator[](int) except +


    cdef _ColourVector _ColourVector_zeros "pyQCD::ColourVector<pyQCD::Real, pyQCD::num_colours>::Zero"()
    cdef _ColourVector _ColourVector_ones "pyQCD::ColourVector<pyQCD::Real, pyQCD::num_colours>::Ones"()


cdef class ColourVector:
    cdef _ColourVector* instance
    cdef int view_count
    cdef Py_ssize_t buffer_shape[1]
    cdef Py_ssize_t buffer_strides[1]

cdef extern from "core/qcd_types.hpp" namespace "pyQCD":
    cdef cppclass _LatticeColourVector "pyQCD::LatticeColourVector<pyQCD::Real, pyQCD::num_colours>":
        _LatticeColourVector() except +
        _LatticeColourVector(const _Layout&, const _ColourVector&, unsigned int site_size) except +
        _ColourVector& operator[](const unsigned int)
        unsigned int volume()
        unsigned int num_dims()
        const vector[unsigned int]& lattice_shape()
        void change_layout(const _Layout&) except +

cdef class LatticeColourVector:
    cdef _LatticeColourVector* instance
    cdef public Layout layout
    cdef bool_t is_buffer_compatible
    cdef int view_count
    cdef public int site_size
    cdef Py_ssize_t buffer_shape[2]
    cdef Py_ssize_t buffer_strides[2]
