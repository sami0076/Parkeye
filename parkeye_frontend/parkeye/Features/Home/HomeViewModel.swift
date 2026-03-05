import Foundation
import CoreLocation

@Observable
class HomeViewModel {
    var selectedPermitType = ""
    var permitTypes: [String] = ["Any", "general", "west_campus", "faculty"]
    var recommendations: [Recommendation] = []
    var isLoading = false
    var errorMessage: String?
    var hasSearched = false
    var arrivalTime = Date()

    private let parkingService: ParkingService
    private let locationService: LocationService

    // GMU campus center fallback
    private let defaultLat = 38.8316
    private let defaultLon = -77.3089

    init(parkingService: ParkingService, locationService: LocationService) {
        self.parkingService = parkingService
        self.locationService = locationService
        self.selectedPermitType = permitTypes[0]
    }

    func reset() {
        recommendations = []
        hasSearched = false
        errorMessage = nil
        selectedPermitType = permitTypes[0]
        arrivalTime = Date()
    }

    func findParking() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            let lat = locationService.currentLocation?.coordinate.latitude ?? defaultLat
            let lon = locationService.currentLocation?.coordinate.longitude ?? defaultLon
            let iso = ISO8601DateFormatter().string(from: arrivalTime)
            recommendations = try await parkingService.fetchRecommendations(
                permit: selectedPermitType,
                destLat: lat,
                destLon: lon,
                arrivalTime: iso
            )
            hasSearched = true
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
