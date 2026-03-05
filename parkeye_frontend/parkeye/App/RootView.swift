import SwiftUI
import Supabase

struct RootView: View {
    @Environment(AppState.self) var appState

    var body: some View {
        Group {
            if appState.isAuthenticated {
                if appState.hasCompletedOnboarding {
                    MainTabView(
                        mapViewModel: appState.mapViewModel,
                        authViewModel: appState.authViewModel,
                        parkingService: appState.parkingService,
                        homeViewModel: appState.homeViewModel,
                        feedbackViewModel: appState.feedbackViewModel,
                        profileViewModel: appState.profileViewModel
                    )
                } else {
                    PermissionsView(locationService: appState.locationService) {
                        appState.hasCompletedOnboarding = true
                    }
                }
            } else {
                WelcomeView(viewModel: appState.authViewModel)
            }
        }
        .task {
            for await (event, session) in appState.supabase.auth.authStateChanges {
                switch event {
                case .initialSession, .signedIn, .tokenRefreshed:
                    appState.isAuthenticated = session != nil
                    appState.currentUser = session?.user
                case .signedOut:
                    appState.isAuthenticated = false
                    appState.currentUser = nil
                    appState.resetAllViewModels()
                default:
                    break
                }
            }
        }
    }
}
