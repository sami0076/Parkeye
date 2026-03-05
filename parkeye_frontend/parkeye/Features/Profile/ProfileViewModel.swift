import Foundation
import Supabase

@Observable
class ProfileViewModel {
    var userEmail: String = ""

    private let supabase: SupabaseClient

    init(supabase: SupabaseClient) {
        self.supabase = supabase
    }

    func loadUser() async {
        if let session = try? await supabase.auth.session {
            userEmail = session.user.email ?? ""
        }
    }

    func reset() {
        userEmail = ""
    }

    func signOut(authViewModel: AuthViewModel) async {
        await authViewModel.signOut()
    }
}
