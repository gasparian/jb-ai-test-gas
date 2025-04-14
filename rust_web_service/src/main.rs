use actix_web::{App, HttpServer};
use rust_web_service::hello_world;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .service(hello_world)
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}