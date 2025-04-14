use actix_web::{get, HttpResponse, Responder};

#[get("/")]
pub async fn hello_world() -> impl Responder {
    HttpResponse::Ok().body("Hello, World!")
}