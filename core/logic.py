import core.state as state
from core.state import check_current_year, stat_state, get_current_energy_level

# Get priority stat from config
def get_stat_priority(stat_key: str) -> int:
  return state.PRIORITY_STAT.index(stat_key) if stat_key in state.PRIORITY_STAT else 999

# Get weighted priority for training decisions
def get_weighted_stat_priority(stat_key: str) -> float:
  """
  Get weighted priority for training decisions using priority weight system.
  Returns a multiplier based on stat priority and weight configuration.
  Higher values indicate higher priority.
  If stat is below min cap, boost weight.
  """
  # Get current stats for min cap logic
  try:
    from core.state import stat_state
    current_stats = stat_state()
  except Exception:
    current_stats = {}
  
  stat_caps = state.STAT_CAPS.get(stat_key, {})
  min_cap = 0
  max_cap = 1200  # default
  if isinstance(stat_caps, dict):
    min_cap = stat_caps.get("min", 0)
    max_cap = stat_caps.get("max", 1200)
  current = current_stats.get(stat_key, 0)
  
  # If below min cap, boost weight (e.g. x2)
  if current < min_cap:
    return 2.0
    
  # Normal weighting with auto-balancing
  priority_index = get_stat_priority(stat_key)
  if priority_index >= len(state.PRIORITY_EFFECTS_LIST):
    return 0.1  # Very low priority for stats not in priority list
  
  base_weight = state.PRIORITY_EFFECTS_LIST[priority_index]
  
  # Auto-balance: higher weight for stats closer to min, lower for those near max
  if max_cap > min_cap:
    balance_factor = (max_cap - current) / (max_cap - min_cap)  # 1.0 at min, 0.0 at max
  else:
    balance_factor = 1.0  # if min == max, no balance
  
  return base_weight * (1.0 + balance_factor)

# Calculate training score with priority weights
def calculate_training_score(stat_key: str, stat_gain: int, support_count: int = 0) -> float:
  """
  Calculate training score using priority weights.
  Combines stat gain with priority multiplier and support card bonus.
  """
  weight = get_weighted_stat_priority(stat_key)
  base_score = stat_gain * weight
  
  # Add bonus for support cards (each support card adds 10% bonus)
  support_bonus = 1.0 + (support_count * 0.1)
  
  return base_score * support_bonus

# Will do train with the most support card
# Used in the first year (aim for rainbow)
def most_support_card(results):
  # Get current energy level for decision making
  energy_level = get_current_energy_level()
  
  # Seperate wit
  wit_data = results.get("wit")

  # Get all training but wit
  non_wit_results = {
    k: v for k, v in results.items()
    if k != "wit" and int(v["failure"]) <= state.MAX_FAILURE
  }

  # Check if train is bad
  all_others_bad = len(non_wit_results) == 0

  if all_others_bad and wit_data and int(wit_data["failure"]) <= state.MAX_FAILURE and wit_data["total_support"] >= 2:
    print("\n[INFO] All trainings are unsafe, but WIT is safe and has enough support cards.")
    return "wit"

  filtered_results = {
    k: v for k, v in results.items() if int(v["failure"]) <= state.MAX_FAILURE
  }

  if not filtered_results:
    print("\n[INFO] No safe training found. All failure chances are too high.")
    return None

  # Best training
  best_training = max(
    filtered_results.items(),
    key=lambda x: (
      x[1]["total_support"],
      -get_stat_priority(x[0])  # priority decides when supports are equal
    )
  )

  best_key, best_data = best_training

  if best_data["total_support"] <= 1:
    if int(best_data["failure"]) == 0:
      # WIT must be at least 2 support cards
      if best_key == "wit":
        # Energy-based decision for WIT training
        if state.ENERGY_DETECTION_ENABLED and energy_level > state.NEVER_REST_ENERGY:
          print(f"\n[INFO] Only 1 support and it's WIT but energy is too high ({energy_level}%) for resting to be worth it. Still training.")
          return "wit"
        else:
          print(f"\n[INFO] Only 1 support and it's WIT. Skipping.")
          return None
      print(f"\n[INFO] Only 1 support but 0% failure. Prioritizing based on priority list: {best_key.upper()}")
      return best_key
    else:
      print("\n[INFO] Low value training (only 1 support). Choosing to rest.")
      return None

  print(f"\nBest training: {best_key.upper()} with {best_data['total_support']} support cards and {best_data['failure']}% fail chance")
  return best_key

# Do rainbow training
def rainbow_training(results):
  # Get rainbow training
  rainbow_candidates = {
    stat: data for stat, data in results.items()
    if int(data["failure"]) <= state.MAX_FAILURE and data["support"].get(stat, 0) > 0
  }

  if not rainbow_candidates:
    print("\n[INFO] No rainbow training found under failure threshold.")
    return None

  # Find support card rainbow in training
  best_rainbow = max(
    rainbow_candidates.items(),
    key=lambda x: (
      x[1]["support"].get(x[0], 0),
      -get_stat_priority(x[0])
    )
  )

  best_key, best_data = best_rainbow
  print(f"\n[INFO] Rainbow training selected: {best_key.upper()} with {best_data['support'][best_key]} rainbow supports and {best_data['failure']}% fail chance")
  return best_key

def filter_by_stat_caps(results, current_stats):
  filtered = {}
  for stat, data in results.items():
    # Support new min/max cap structure
    stat_caps = state.STAT_CAPS.get(stat, {})
    if isinstance(stat_caps, dict):
      max_cap = stat_caps.get("max", 1200)
    else:
      max_cap = stat_caps  # fallback for old config
    current = current_stats.get(stat, 0)
    
    # Ensure max_cap is a number
    if isinstance(max_cap, dict):
      max_cap = max_cap.get("max", 1200)  # Handle nested dict case
    
    if current < max_cap:
      filtered[stat] = data
  return filtered
  # ...existing code...

# Enhanced weighted training decision using priority weights
def weighted_training_decision(results):
  """
  Make training decisions using the priority weight system.
  Calculates weighted scores for each training option.
  """
  energy_level = get_current_energy_level()
  # Filter out unsafe trainings
  safe_trainings = {
    k: v for k, v in results.items() 
    if int(v["failure"]) <= state.MAX_FAILURE
  }
  if not safe_trainings:
    print("\n[INFO] No safe training found with priority weight system.")
    return None
  # Calculate weighted scores for each training
  training_scores = {}
  for stat_key, training_data in safe_trainings.items():
    # Get expected stat gain (use a reasonable estimate if not available)
    stat_gain = training_data.get("stat_gain", 10)  # Default estimate
    support_count = training_data.get("total_support", 0)
    # Calculate weighted score
    score = calculate_training_score(stat_key, stat_gain, support_count)
    training_scores[stat_key] = {
      "score": score,
      "data": training_data,
      "priority_weight": get_weighted_stat_priority(stat_key)
    }
    print(f"[WEIGHT] {stat_key.upper()}: Score={score:.2f} (Weight={get_weighted_stat_priority(stat_key):.2f}, Supports={support_count}, Failure={training_data['failure']}%)")
  # Special handling for WIT training (needs at least 2 supports)
  if "wit" in training_scores:
    wit_data = training_scores["wit"]["data"]
    if wit_data["total_support"] < 2 and len([k for k in training_scores.keys() if k != "wit"]) > 0:
      print(f"[WEIGHT] WIT has insufficient supports ({wit_data['total_support']}), reducing score")
      training_scores["wit"]["score"] *= 0.5
  # Find best training by weighted score
  best_stat = max(training_scores.items(), key=lambda x: x[1]["score"])
  best_key = best_stat[0]
  best_info = best_stat[1]
  print(f"\n[WEIGHT] Best weighted training: {best_key.upper()} (Score: {best_info['score']:.2f}, Weight: {best_info['priority_weight']:.2f})")
  return best_key
  safe_trainings = {
    k: v for k, v in results.items() 
    if int(v["failure"]) <= state.MAX_FAILURE
  }
  
  if not safe_trainings:
    print("\n[INFO] No safe training found with priority weight system.")
    return None
    
  # Calculate weighted scores for each training
  training_scores = {}
  for stat_key, training_data in safe_trainings.items():
    # Get expected stat gain (use a reasonable estimate if not available)
    stat_gain = training_data.get("stat_gain", 10)  # Default estimate
    support_count = training_data.get("total_support", 0)
    
    # Calculate weighted score
    score = calculate_training_score(stat_key, stat_gain, support_count)
    training_scores[stat_key] = {
      "score": score,
      "data": training_data,
      "priority_weight": get_weighted_stat_priority(stat_key)
    }
    
    print(f"[WEIGHT] {stat_key.upper()}: Score={score:.2f} (Weight={get_weighted_stat_priority(stat_key):.2f}, Supports={support_count}, Failure={training_data['failure']}%)")
  
  # Special handling for WIT training (needs at least 2 supports)
  if "wit" in training_scores:
    wit_data = training_scores["wit"]["data"]
    if wit_data["total_support"] < 2 and len([k for k in training_scores.keys() if k != "wit"]) > 0:
      print(f"[WEIGHT] WIT has insufficient supports ({wit_data['total_support']}), reducing score")
      training_scores["wit"]["score"] *= 0.5
  
  # Find best training by weighted score
  best_stat = max(training_scores.items(), key=lambda x: x[1]["score"])
  best_key = best_stat[0]
  best_info = best_stat[1]
  
  print(f"\n[WEIGHT] Best weighted training: {best_key.upper()} (Score: {best_info['score']:.2f}, Weight: {best_info['priority_weight']:.2f})")
  return best_key
  
# Decide training
def do_something(results):
  year = check_current_year()
  current_stats = stat_state()
  energy_level = get_current_energy_level()
  
  print(f"Current stats: {current_stats}")
  if state.ENERGY_DETECTION_ENABLED:
    print(f"Current energy: {energy_level}%")

  # Energy-based pre-checks
  if state.ENERGY_DETECTION_ENABLED:
    # Skip training if energy is too low
    if energy_level < state.SKIP_TRAINING_ENERGY:
      print(f"\n[INFO] Energy too low ({energy_level}% < {state.SKIP_TRAINING_ENERGY}%). Choosing to rest.")
      return None
      
    # If energy is very high, prioritize training even with fewer supports
    if energy_level > state.NEVER_REST_ENERGY:
      print(f"\n[INFO] Energy is high ({energy_level}% > {state.NEVER_REST_ENERGY}%). Will be more aggressive with training choices.")

  filtered = filter_by_stat_caps(results, current_stats)

  if not filtered:
    print("[INFO] All stats capped or no valid training.")
    return None

  # Use priority weight system if enabled (regardless of year)
  if state.PRIORITY_WEIGHT != "DISABLED":
    print(f"\n[INFO] Using priority weight system (Level: {state.PRIORITY_WEIGHT})")
    return weighted_training_decision(filtered)

  # Original logic for when priority weights are disabled  
  if "Junior Year" in year:
    return most_support_card(filtered)
  else:
    result = rainbow_training(filtered)
    if result is None:
      print("[INFO] Falling back to most_support_card because rainbow not available.")
      return most_support_card(filtered)
  return result
