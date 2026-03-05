import Foundation

enum APIError: Error {
    case invalidURL
    case unauthorized
    case httpError(statusCode: Int)
    case decodingError(Error)
    case networkError(Error)
}
