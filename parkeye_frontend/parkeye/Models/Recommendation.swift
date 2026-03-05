import Foundation

struct Recommendation: Decodable, Identifiable {
    let id: UUID
    let lotName: String
    let occupancyPct: Double
    let color: String
    let walkMinutes: Double?
    let confidence: String?
    let permitTypes: [String]?

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        // APIClient uses convertFromSnakeCase: "lot_id" → "lotId", "predicted_pct" → "predictedPct", etc.
        id = try c.decode(UUID.self, forKey: .lotId)
        lotName = try c.decode(String.self, forKey: .name)
        let pct = try c.decode(Double.self, forKey: .predictedPct)
        occupancyPct = pct * 100
        color = hexFromSemanticColor(try c.decode(String.self, forKey: .color))
        walkMinutes = try c.decodeIfPresent(Double.self, forKey: .walkMinutes)
        confidence = try c.decodeIfPresent(String.self, forKey: .confidence)
        permitTypes = try c.decodeIfPresent([String].self, forKey: .permitTypes)
    }

    private enum CodingKeys: CodingKey {
        case lotId, name, predictedPct, color, walkMinutes, confidence, permitTypes
    }
}

struct RecommendationsResponse: Decodable {
    let recommendations: [Recommendation]
}
