use dotenvy::{dotenv, var};

use crate::domain::models::config::Config;
use crate::infrastructure::parser::config_parser::ConfigParser;

pub struct EnvConfigParser;

impl ConfigParser for EnvConfigParser {
    fn parse() -> Result<Config, &'static str> {
        let _ = dotenv();

        Ok(Config {
            codeforces_oauth_client_id: var("CODEFORCES_OAUTH_CLIENT_ID").map_err(|_| "CODEFORCES_OAUTH_CLIENT_ID variable not found")?,
            codeforces_oauth_client_secret: var("CODEFORCES_OAUTH_CLIENT_SECRET").map_err(|_| "CODEFORCES_OAUTH_CLIENT_SECRET variable not found")?,
        })
    }
}