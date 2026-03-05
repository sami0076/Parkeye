import Foundation

enum APIEndpoints {
    static var baseURL: URL {
        URL(string: Bundle.main.object(forInfoDictionaryKey: "API_BASE_URL") as! String)!
    }

    static var wsBaseURL: URL {
        URL(string: Bundle.main.object(forInfoDictionaryKey: "WS_BASE_URL") as! String)!
    }

    static var lots: URL { baseURL.appending(path: "lots") }
    static func lot(id: UUID) -> URL { baseURL.appending(path: "lots/\(id)") }
    static func lotHistory(id: UUID) -> URL { baseURL.appending(path: "lots/\(id)/history") }
    static func predictions(lotId: UUID) -> URL { baseURL.appending(path: "predictions/\(lotId)") }
    static func recommendations(
        permit: String,
        destLat: Double,
        destLon: Double,
        arrivalTime: String,
        durationMin: Int? = nil
    ) -> URL {
        var components = URLComponents(url: baseURL.appending(path: "recommendations"), resolvingAgainstBaseURL: false)!
        var queryItems: [URLQueryItem] = [
            URLQueryItem(name: "dest_lat", value: String(destLat)),
            URLQueryItem(name: "dest_lon", value: String(destLon)),
            URLQueryItem(name: "arrival_time", value: arrivalTime),
        ]
        if !permit.isEmpty && permit != "Any" {
            queryItems.append(URLQueryItem(name: "permit_type", value: permit))
        }
        if let dur = durationMin { queryItems.append(URLQueryItem(name: "duration_min", value: String(dur))) }
        components.queryItems = queryItems
        return components.url!
    }
    static var feedback: URL { baseURL.appending(path: "feedback") }
    static var wsOccupancy: URL { wsBaseURL.appending(path: "ws/occupancy") }
}
