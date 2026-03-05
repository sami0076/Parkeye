import Foundation

@Observable
class FeedbackViewModel {
    var selectedLotId: UUID?
    var accuracyRating: Int = 0
    var experienceRating: Int = 0
    var note: String = ""
    var isLoading = false
    var isSubmitted = false
    var errorMessage: String?

    private let parkingService: ParkingService

    init(parkingService: ParkingService) {
        self.parkingService = parkingService
    }

    func submit() async {
        guard let lotId = selectedLotId, accuracyRating > 0, experienceRating > 0 else {
            errorMessage = "Please select a lot and provide both ratings."
            return
        }
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        let request = FeedbackRequest(
            lotId: lotId,
            accuracyRating: accuracyRating,
            experienceRating: experienceRating,
            note: note.isEmpty ? nil : note
        )
        do {
            try await parkingService.submitFeedback(request)
            isSubmitted = true
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func reset() {
        selectedLotId = nil
        accuracyRating = 0
        experienceRating = 0
        note = ""
        isSubmitted = false
        errorMessage = nil
    }
}
