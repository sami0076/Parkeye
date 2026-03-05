import SwiftUI
import Supabase

@main
struct parkeyeApp: App {
    @State private var appState: AppState

    init() {
        let urlString = Bundle.main.object(forInfoDictionaryKey: "SUPABASE_URL") as! String
        let key = Bundle.main.object(forInfoDictionaryKey: "SUPABASE_ANON_KEY") as! String
        let url = URL(string: urlString)!
        _appState = State(initialValue: AppState(supabase: SupabaseClient(supabaseURL: url, supabaseKey: key)))
    }

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(appState)
        }
    }
}
