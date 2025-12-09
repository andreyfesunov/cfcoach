use crate::domain::models::config::Config;

pub trait ConfigParser {
    fn parse() -> Result<Config, &'static str>;
}