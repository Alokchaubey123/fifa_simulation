import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


SEED = 2026
N_SIMULATIONS = 10000  # This is no. of simulations between two teams
BASE_LAMBDA = 1.35   # This is the average expected goals in one match before adjusting for team strength.
DEFENCE_FLOOR = 0.30 # This is the average defense for the goals by a team 

rng = np.random.default_rng(SEED)


teams = {
  
    "France": {
        "GF": 16,
        "GA": 2,
        "MP": 6
    },

    "Spain": {
        "GF": 11,
        "GA": 1,
        "MP": 6
    },

    "England": {
        "GF": 13,
        "GA": 6,
        "MP": 6
    },

    "Argentina": {
        "GF": 17,
        "GA": 6,
        "MP": 6
    }
}

semi_finals = [
    ("France", "Spain"),
    ("England", "Argentina")
]


# Team strength table

team_df = pd.DataFrame.from_dict(teams, orient="index")
team_df.index.name = "Team"

team_df["GF_pg"] = team_df["GF"] / team_df["MP"] #GF_pg means Goals For Per Game

team_df["GA_pg"] = team_df["GA"] / team_df["MP"] #GA_pg means Goals Against Per Game

avg_gf_pg = team_df["GF_pg"].mean()
avg_ga_pg = team_df["GA_pg"].mean()

# Higher AttackStrength = better attack
team_df["AttackStrength"] = team_df["GF_pg"] / avg_gf_pg # AttackStrength = Goals per Game​ / Average Goals per Game

# Lower DefenceWeakness = better defence
team_df["DefenceWeakness"] = team_df["GA_pg"] / avg_ga_pg
team_df["DefenceWeakness"] = team_df["DefenceWeakness"].clip(lower=DEFENCE_FLOOR) # DefenceWeakness cannot go below 0.30


# Match model


def expected_goals(team_a, team_b):
    """Calculate expected goals for a match using attack and defence strengths."""

    lambda_a = (
        BASE_LAMBDA
        * team_df.loc[team_a, "AttackStrength"]
        * team_df.loc[team_b, "DefenceWeakness"]
    )

    lambda_b = (
        BASE_LAMBDA
        * team_df.loc[team_b, "AttackStrength"]
        * team_df.loc[team_a, "DefenceWeakness"]
    )

    return float(lambda_a), float(lambda_b)


def penalty_win_probability(team_a, team_b):
    """Penalty edge based on attack/defence balance if simulated goals are level."""

    a_balance = team_df.loc[team_a, "AttackStrength"] / team_df.loc[team_a, "DefenceWeakness"]
    b_balance = team_df.loc[team_b, "AttackStrength"] / team_df.loc[team_b, "DefenceWeakness"]

    return float(a_balance / (a_balance + b_balance))


def play_knockout_match(team_a, team_b):
    """Simulate one knockout match. If goals are equal, decide by penalties."""

    lambda_a, lambda_b = expected_goals(team_a, team_b)

    goals_a = rng.poisson(lambda_a)
    goals_b = rng.poisson(lambda_b)

    if goals_a > goals_b:
        return team_a, goals_a, goals_b, False

    if goals_b > goals_a:
        return team_b, goals_a, goals_b, False

    # Penalty shootout after draw
    p_a = penalty_win_probability(team_a, team_b)
    winner = team_a if rng.random() < p_a else team_b

    return winner, goals_a, goals_b, True


def simulate_semi_final(team_a, team_b, n=N_SIMULATIONS):
    """Run one semi-final n times."""

    wins = {
        team_a: 0,
        team_b: 0
    }

    draws_to_pens = 0
    total_goals_a = 0
    total_goals_b = 0

    for _ in range(n):
        winner, goals_a, goals_b, went_to_pens = play_knockout_match(team_a, team_b)

        wins[winner] += 1
        total_goals_a += goals_a
        total_goals_b += goals_b

        if went_to_pens:
            draws_to_pens += 1

    lambda_a, lambda_b = expected_goals(team_a, team_b)

    predicted_winner = team_a if wins[team_a] > wins[team_b] else team_b

    return {
        "Match": f"{team_a} vs {team_b}",
        "Team_A": team_a,
        "Team_B": team_b,
        "Team_A_xG": round(lambda_a, 2),
        "Team_B_xG": round(lambda_b, 2),
        "Team_A_AvgGoalsSim": round(total_goals_a / n, 2),
        "Team_B_AvgGoalsSim": round(total_goals_b / n, 2),
        "Team_A_Wins": wins[team_a],
        "Team_B_Wins": wins[team_b],
        "Team_A_Win_%": round(wins[team_a] / n * 100, 2),
        "Team_B_Win_%": round(wins[team_b] / n * 100, 2),
        "Pens_%": round(draws_to_pens / n * 100, 2),
        "Predicted_Winner": predicted_winner
    }



semi_results = []

for team_a, team_b in semi_finals:
    semi_results.append(simulate_semi_final(team_a, team_b))

semi_df = pd.DataFrame(semi_results)



print("\n================ SEMI-FINALS: 10,000 SIMULATIONS EACH ================")
print(semi_df.to_string(index=False))

print("\n================ PREDICTED SEMI-FINAL WINNERS ================")
for _, row in semi_df.iterrows():
    print(row["Match"] + " -> " + row["Predicted_Winner"])


semi_df.to_csv("semis_10000_updated_webdata_results.csv", index=False)
team_df.to_csv("semis_10000_updated_webdata_team_form.csv")

plot_rows = []

for _, row in semi_df.iterrows():
    plot_rows.append({
        "Label": row["Match"] + " | " + row["Team_A"],
        "Win_%": row["Team_A_Win_%"]
    })
    plot_rows.append({
        "Label": row["Match"] + " | " + row["Team_B"],
        "Win_%": row["Team_B_Win_%"]
    })

plot_df = pd.DataFrame(plot_rows)

plt.figure(figsize=(10, 5))
plt.barh(plot_df["Label"], plot_df["Win_%"])
plt.xlabel("Win Probability (%)")
plt.title("FIFA World Cup 2026 Semi-finals - Updated Web Data, 10,000 Sims")

for i, value in enumerate(plot_df["Win_%"]):
    plt.text(value + 0.5, i, f"{value:.2f}%", va="center")

plt.tight_layout()
plt.savefig("semis_10000_updated_webdata_plot.png", dpi=160)
plt.show()
