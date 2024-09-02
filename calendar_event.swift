import EventKit
import Foundation
import Dispatch

@_cdecl("create_calendar_event")
public func createCalendarEvent(title: UnsafePointer<CChar>, startDate: Double, endDate: Double, addAlarm: Bool, repeatWeekly: Bool) {
    let eventStore = EKEventStore()
    let semaphore = DispatchSemaphore(value: 0)  

    eventStore.requestFullAccessToEvents { (granted, error) in
        if granted && error == nil {
            let event = EKEvent(eventStore: eventStore)
            
            if let titleStr = String(validatingUTF8: title) {
                event.title = titleStr
            } else {
                print("Error: Failed to decode title string")
                semaphore.signal()
                return
            }
            
            event.startDate = Date(timeIntervalSince1970: startDate)
            event.endDate = Date(timeIntervalSince1970: endDate)
            event.calendar = eventStore.defaultCalendarForNewEvents
            
            if addAlarm {
                let alarm = EKAlarm(relativeOffset: -30 * 60)  
                event.addAlarm(alarm)
            }
            
            if repeatWeekly {
                let recurrenceRule = EKRecurrenceRule(recurrenceWith: .weekly, interval: 1, end: nil)
                event.addRecurrenceRule(recurrenceRule)
            }
            
            do {
                try eventStore.save(event, span: .thisEvent, commit: true)
                print("Event saved successfully: \(event.title ?? "Unnamed Event")")
            } catch let error {
                print("Failed to save event with error: \(error)")
            }
        } else {
            print("Access denied or error occurred: \(String(describing: error))")
        }
        semaphore.signal() 
    }
    
    semaphore.wait() 
}
