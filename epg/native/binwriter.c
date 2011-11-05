/* 
 * Copyright 2011 Synesis LLC.
 *
 * Technical support and updates: http://synet.synesis.ru
 * You are free to use this software for evaluation and commercial purposes
 * under condition that it is used only in conjunction with digital TV
 * receivers running SYNET middleware by Synesis.
 *
 * To contribute modifcations, additional modules and derived works please
 * contact pnx@synesis.ru
 */

#include <Python.h>
#include <stdio.h>
#include <string.h>

#define UINT_TYPE 5
#define STRING_TYPE 12

static char *pystr2cstr(PyObject *str)
{
    char *res = NULL;
    int len;
    if (PyString_Check(str))
    {
        len = PyString_Size(str);
        res = malloc(len + 1);
        memcpy(res, PyString_AsString(str), len);
        res[len] = 0;
    }
    else if (PyUnicode_Check(str))
    {
        PyObject *repr = PyUnicode_AsUTF8String(str);
        len = PyString_Size(repr);
        res = malloc(len + 1);
        memcpy(res, PyString_AsString(repr), len);
        res[len] = 0;
        Py_XDECREF(repr);
    }

    return res;
}

static int pack_uint(unsigned char **buf_ptr, unsigned buflen, unsigned val)
{
    if (buflen < 4)
        return 0;

    **buf_ptr = (val >> 0) & 0xff;
    (*buf_ptr)++;
    **buf_ptr = (val >> 8) & 0xff;
    (*buf_ptr)++;
    **buf_ptr = (val >> 16) & 0xff;
    (*buf_ptr)++;
    **buf_ptr = (val >> 24) & 0xff;
    (*buf_ptr)++;

    return 4;
}

static int pack_string(unsigned char **buf_ptr, unsigned buflen, const char *str)
{
    int len = strlen(str);

    if (buflen < len + 4 + 1)
        return 0;

    pack_uint(buf_ptr, buflen, len + 1);
    strcpy((char *)*buf_ptr, str);

    (*buf_ptr) += len + 1;

    return len + 4 + 1;
}

static PyObject *row2bin(PyObject *self, PyObject *args)
{
    unsigned char buf[65536];
    unsigned char *buf_ptr = buf;
    int len = 0;
    PyObject *row;
    PyObject *key, *value;
    Py_ssize_t pos;

    if (!PyArg_ParseTuple(args, "O:row2bin", &row))
        return NULL;

    if (!PyDict_Check(row))
    {
        PyErr_SetString(PyExc_TypeError,
            "expected argument of dict type");
        return NULL;
    }

    len += pack_uint(&buf_ptr, sizeof(buf) - len, (unsigned)PyDict_Size(row));

    pos = 0;
    while (PyDict_Next(row, &pos, &key, &value))
    {

        char *key_str = pystr2cstr(key);

        if (!key_str)
        {
            PyErr_SetString(PyExc_TypeError,
                "expected dict keys of <str> or <unicode> type");
            return NULL;
        }
        len += pack_string(&buf_ptr, sizeof(buf) - len, key_str);
        free(key_str);

        if (PyString_Check(value) || PyUnicode_Check(value))
        {
            char *value_str = pystr2cstr(value);
            len += pack_uint(&buf_ptr, sizeof(buf) - len, STRING_TYPE);
            len += pack_string(&buf_ptr, sizeof(buf) - len, value_str);
            free(value_str);
        }
        else if (PyInt_Check(value))
        {
            len += pack_uint(&buf_ptr, sizeof(buf) - len, UINT_TYPE);
            len += pack_uint(&buf_ptr, sizeof(buf) - len, PyInt_AsLong(value));
        }
        else if (PyLong_Check(value))
        {
            len += pack_uint(&buf_ptr, sizeof(buf) - len, UINT_TYPE);
            len += pack_uint(&buf_ptr, sizeof(buf) - len, PyLong_AsLong(value));
        }
        else
        {
            PyErr_SetString(PyExc_TypeError,
                "expected dict values of <int> or <unicode> or <str> type");
            return NULL;
        }
    }

    return Py_BuildValue("s#", (char *)buf, len);
}

static PyMethodDef binWriterMethods[] = 
{
    {"row2bin", row2bin, METH_VARARGS, "Convert row (in dict) into SyNET binary format"},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initbinwriter(void)
{
    (void)Py_InitModule("binwriter", binWriterMethods);
}
