import Foundation
import Supabase

@Observable
class AuthViewModel {
    var email = ""
    var password = ""
    var isLoading = false
    var errorMessage: String?
    var needsEmailConfirmation = false

    private let supabase: SupabaseClient

    init(supabase: SupabaseClient) {
        self.supabase = supabase
    }

    func signIn() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            try await supabase.auth.signIn(email: email, password: password)
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func signUp() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }
        do {
            let response = try await supabase.auth.signUp(email: email, password: password)
            // session is nil when email confirmation is required
            if response.session == nil {
                needsEmailConfirmation = true
            }
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func signOut() async {
        try? await supabase.auth.signOut()
    }
}
