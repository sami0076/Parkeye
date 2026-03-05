import Foundation

struct Lot: Decodable, Identifiable {
    let id: UUID
    let name: String
    var occupancyPct: Double
    var color: String
    let capacity: Int
    let permitTypes: [String]?
    let lat: Double
    let lon: Double
    let isDeck: Bool
    let floors: Int?
    let status: String?
    let statusUntil: Date?
    let statusReason: String?

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try c.decode(UUID.self, forKey: .id)
        name = try c.decode(String.self, forKey: .name)
        let pct = try c.decode(Double.self, forKey: .occupancyPct)
        occupancyPct = pct * 100
        color = hexFromSemanticColor(try c.decode(String.self, forKey: .color))
        capacity = try c.decode(Int.self, forKey: .capacity)
        permitTypes = try c.decodeIfPresent([String].self, forKey: .permitTypes)
        lat = try c.decode(Double.self, forKey: .lat)
        lon = try c.decode(Double.self, forKey: .lon)
        isDeck = try c.decode(Bool.self, forKey: .isDeck)
        floors = try c.decodeIfPresent(Int.self, forKey: .floors)
        status = try c.decodeIfPresent(String.self, forKey: .status)
        statusUntil = try c.decodeIfPresent(Date.self, forKey: .statusUntil)
        statusReason = try c.decodeIfPresent(String.self, forKey: .statusReason)
    }

    private enum CodingKeys: CodingKey {
        case id, name, occupancyPct, color, capacity, permitTypes
        case lat, lon, isDeck, floors, status, statusUntil, statusReason
    }
}
