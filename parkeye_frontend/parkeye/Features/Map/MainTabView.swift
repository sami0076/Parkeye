import SwiftUI

struct MainTabView: View {
    @Bindable var mapViewModel: MapViewModel
    var authViewModel: AuthViewModel
    var parkingService: ParkingService
    var homeViewModel: HomeViewModel
    var feedbackViewModel: FeedbackViewModel
    var profileViewModel: ProfileViewModel

    var body: some View {
        TabView {
            ParkeyeMapView(viewModel: mapViewModel)
                .ignoresSafeArea()
                .tabItem { Label("Map", systemImage: "map") }

            HomeView(viewModel: homeViewModel)
                .tabItem { Label("Home", systemImage: "house") }

            FeedbackView(viewModel: feedbackViewModel, lots: mapViewModel.lots)
                .tabItem { Label("Feedback", systemImage: "star") }

            ProfileView(viewModel: profileViewModel, authViewModel: authViewModel)
                .tabItem { Label("Profile", systemImage: "person.circle") }
        }
        .task { await mapViewModel.loadLots() }
        .task { await mapViewModel.connectLiveOccupancy() }
        .sheet(item: $mapViewModel.selectedLot) { lot in
            LotDetailSheet(lotId: lot.id, parkingService: parkingService)
        }
    }
}
