import Foundation
import Supabase

@Observable @MainActor
class AppState {
    var isAuthenticated = false
    var currentUser: User?
    var hasCompletedOnboarding: Bool {
        get { UserDefaults.standard.bool(forKey: "hasCompletedOnboarding") }
        set { UserDefaults.standard.set(newValue, forKey: "hasCompletedOnboarding") }
    }

    let supabase: SupabaseClient
    let authViewModel: AuthViewModel
    let mapViewModel: MapViewModel
    let parkingService: ParkingService
    let locationService: LocationService
    let homeViewModel: HomeViewModel
    let feedbackViewModel: FeedbackViewModel
    let profileViewModel: ProfileViewModel

    func resetAllViewModels() {
        feedbackViewModel.reset()
        homeViewModel.reset()
        profileViewModel.reset()
    }

    init(supabase: SupabaseClient) {
        self.supabase = supabase
        let apiClient = APIClient(supabase: supabase)
        let parkingService = ParkingService(apiClient: apiClient)
        let webSocketClient = WebSocketClient(url: APIEndpoints.wsOccupancy)
        self.parkingService = parkingService
        self.authViewModel = AuthViewModel(supabase: supabase)
        self.mapViewModel = MapViewModel(parkingService: parkingService, webSocketClient: webSocketClient)
        self.locationService = LocationService()
        self.homeViewModel = HomeViewModel(parkingService: parkingService, locationService: locationService)
        self.feedbackViewModel = FeedbackViewModel(parkingService: parkingService)
        self.profileViewModel = ProfileViewModel(supabase: supabase)
    }
}
