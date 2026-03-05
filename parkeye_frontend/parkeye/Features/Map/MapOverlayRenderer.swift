import MapKit
import SwiftUI

final class LotPolygonRenderer: MKPolygonRenderer {
    func configure(hexColor: String) {
        fillColor = UIColor(Color(hex: hexColor)).withAlphaComponent(0.45)
        strokeColor = UIColor(Color(hex: hexColor))
        lineWidth = 1.5
    }

    func updateColor(hexColor: String) {
        fillColor = UIColor(Color(hex: hexColor)).withAlphaComponent(0.45)
        strokeColor = UIColor(Color(hex: hexColor))
        setNeedsDisplay()
    }
}
