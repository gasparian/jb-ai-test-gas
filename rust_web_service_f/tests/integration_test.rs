use reqwest::Client;
use std::net::TcpListener;
use actix_web::{App, HttpServer};
use rust_web_service_f_lib::hello_world;
use tokio::task::JoinHandle;

async fn spawn_app() -> (String, JoinHandle<Result<(), std::io::Error>>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("Failed to bind random port");
    let port = listener.local_addr().unwrap().port();
    
    let server = HttpServer::new(|| {
        App::new()
            .service(hello_world)
    })
    .listen(listener)
    .expect("Failed to start server")
    .run();

    // Spawn the server and keep the handle
    let handle = tokio::spawn(server);

    let address = format!("http://127.0.0.1:{}", port);
    (address, handle)
}

#[tokio::test]
async fn test_hello_world() {
    // Spawn the app and get the address and server handle
    let (address, handle) = spawn_app().await;
    let client = Client::new();

    // Make async HTTP request
    let response = client.get(&address).send().await.expect("Failed to send request");

    // Verify response
    assert_eq!(response.status(), 200);
    assert_eq!(response.text().await.unwrap(), "Hello, World!");

    // Shut down the server
    handle.abort();
}