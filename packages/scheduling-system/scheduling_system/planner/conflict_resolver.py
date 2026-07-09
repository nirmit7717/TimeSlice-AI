from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple
from scheduling_system.models.time_slice import TimeSlice

class ConflictResolver:
    def resolve_conflicts(self, slices: List[TimeSlice], context: Dict[str, Any]) -> List[TimeSlice]:
        """
        Shifts slices sequentially to resolve overlaps with blocked calendar intervals.
        """
        blocked_intervals = context.get("blocked_intervals", [])
        if not slices:
            return []

        # Sort slices and blocked intervals chronologically
        sorted_slices = sorted(slices, key=lambda s: s.start_time)
        sorted_blocks = sorted(blocked_intervals, key=lambda b: b[0])

        resolved_slices = []
        for s in sorted_slices:
            slice_dur = timedelta(hours=s.duration_hours)
            slice_start = s.start_time
            if slice_start.tzinfo is None:
                slice_start = slice_start.replace(tzinfo=timezone.utc)
                
            slice_end = slice_start + slice_dur

            # Loop and shift slice as long as it overlaps with any blocked intervals
            shifted = True
            while shifted:
                shifted = False
                for b_start, b_end in sorted_blocks:
                    if b_start.tzinfo is None:
                        b_start = b_start.replace(tzinfo=timezone.utc)
                    if b_end.tzinfo is None:
                        b_end = b_end.replace(tzinfo=timezone.utc)
                        
                    # Check overlap: slice_end > b_start and slice_start < b_end
                    if slice_end > b_start and slice_start < b_end:
                        # Shift start to end of block
                        slice_start = b_end
                        slice_end = slice_start + slice_dur
                        shifted = True
                        break # Break loop to restart checks from the first block with the new timing
            
            s.start_time = slice_start
            s.end_time = slice_end
            resolved_slices.append(s)
            
            # Treat resolved slices as temporary blockages for subsequent slices to prevent overlaps!
            sorted_blocks.append((slice_start, slice_end))
            sorted_blocks = sorted(sorted_blocks, key=lambda b: b[0])

        return resolved_slices
