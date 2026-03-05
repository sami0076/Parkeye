import Foundation

struct FeedbackRequest: Encodable {
    let lotId: UUID
    let accuracyRating: Int
    let experienceRating: Int
    let note: String?
}
