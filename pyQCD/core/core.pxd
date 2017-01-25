from cpython cimport Py_buffer

from libcpp.vector cimport vector

from atomics cimport Real, Complex

cdef extern from "core/layout.hpp" namespace "pyQCD":
    cdef cppclass Layout:
        Layout()
        unsigned int get_array_index(const unsigned int)
        unsigned int get_array_index(const vector[unsigned int]&)
        unsigned int get_site_index(const unsigned int)
        unsigned int num_dims()
        unsigned int volume()
        const vector[unsigned int]& shape()

    cdef cppclass LexicoLayout(Layout):
        LexicoLayout() except+
        LexicoLayout(const vector[unsigned int]&) except+



cdef extern from "core/types.hpp" namespace "pyQCD::python":
    cdef cppclass _ColourMatrix "pyQCD::python::ColourMatrix":
        _ColourMatrix() except +
        _ColourMatrix(const _ColourMatrix&) except +
        _ColourMatrix adjoint()
        Complex& operator()(int, int) except +


    cdef _ColourMatrix _ColourMatrix_zeros "pyQCD::python::ColourMatrix::Zero"()
    cdef _ColourMatrix _ColourMatrix_ones "pyQCD::python::ColourMatrix::Ones"()

cdef extern from "utils/matrices.hpp" namespace "pyQCD":
    cdef _ColourMatrix _random_colour_matrix "pyQCD::random_sun<pyQCD::Real, pyQCD::num_colours>"()

cdef class ColourMatrix:
    cdef _ColourMatrix* instance
    cdef int view_count
    cdef Py_ssize_t buffer_shape[2]
    cdef Py_ssize_t buffer_strides[2]

cdef extern from "core/types.hpp" namespace "pyQCD::python":
    cdef cppclass _LatticeColourMatrix "pyQCD::python::LatticeColourMatrix":
        _LatticeColourMatrix() except +
        _LatticeColourMatrix(const Layout&, const _ColourMatrix&, unsigned int site_size) except +
        _ColourMatrix& operator[](const unsigned int)
        unsigned int volume()
        unsigned int num_dims()
        const vector[unsigned int]& lattice_shape()

cdef class LatticeColourMatrix:
    cdef _LatticeColourMatrix* instance
    cdef Layout* lexico_layout
    cdef int view_count
    cdef int site_size
    cdef Py_ssize_t buffer_shape[3]
    cdef Py_ssize_t buffer_strides[3]

cdef extern from "core/types.hpp" namespace "pyQCD::python":
    cdef cppclass _ColourVector "pyQCD::python::ColourVector":
        _ColourVector() except +
        _ColourVector(const _ColourVector&) except +
        _ColourVector adjoint()
        Complex& operator[](int) except +


    cdef _ColourVector _ColourVector_zeros "pyQCD::python::ColourVector::Zero"()
    cdef _ColourVector _ColourVector_ones "pyQCD::python::ColourVector::Ones"()


cdef class ColourVector:
    cdef _ColourVector* instance
    cdef int view_count
    cdef Py_ssize_t buffer_shape[1]
    cdef Py_ssize_t buffer_strides[1]

cdef extern from "core/types.hpp" namespace "pyQCD::python":
    cdef cppclass _LatticeColourVector "pyQCD::python::LatticeColourVector":
        _LatticeColourVector() except +
        _LatticeColourVector(const Layout&, const _ColourVector&, unsigned int site_size) except +
        _ColourVector& operator[](const unsigned int)
        unsigned int volume()
        unsigned int num_dims()
        const vector[unsigned int]& lattice_shape()

cdef class LatticeColourVector:
    cdef _LatticeColourVector* instance
    cdef Layout* lexico_layout
    cdef int view_count
    cdef int site_size
    cdef Py_ssize_t buffer_shape[2]
    cdef Py_ssize_t buffer_strides[2]
