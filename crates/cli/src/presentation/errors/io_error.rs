use std::io::{Error, ErrorKind};
use std::ops::Deref;

#[derive(Debug)]
pub struct IoError(Error);

impl IoError {
    fn new(p0: ErrorKind, p1: &str) -> IoError {
        IoError(Error::new(p0, p1))
    }
}

impl Deref for IoError {
    type Target = Error;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl From<&'static str> for IoError {
    fn from(value: &'static str) -> Self {
        IoError::new(ErrorKind::Other, value)
    }
}