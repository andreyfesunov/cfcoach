mod presentation;

use config::infrastructure::parser::config_parser::ConfigParser;
use config::infrastructure::parser::env_config_parser::EnvConfigParser;
use crate::presentation::errors::io_error::IoError;

fn main() -> Result<(), IoError> {
    let config = EnvConfigParser::parse()?;

    println!("{:#?}", config);

    Ok(())
}
