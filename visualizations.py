"""
visualizations.py
Generate visualizations for authorization test results.
Creates heat maps, bar charts, and summary graphics.
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path


class TestResultVisualizer:
    """
    Creates professional visualizations from test results.
    """

    def __init__(self, json_file='test_results.json'):
        """Load test results from JSON file"""
        with open(json_file, 'r') as f:
            data = json.load(f)

        self.summary = data['summary']
        self.results = pd.DataFrame(data['results'])

        # Create output directory
        Path('visualizations').mkdir(exist_ok=True)

        print(f"📊 Loaded {len(self.results)} test results")
        print(f"   Pass rate: {self.summary['pass_rate']:.1f}%")

    def create_overall_summary(self):
        """Create a summary bar chart of pass/fail"""
        fig, ax = plt.subplots(figsize=(10, 6))

        categories = ['Passed', 'Failed']
        values = [self.summary['passed'], self.summary['failed']]
        colors = ['#4CAF50', '#F44336']

        bars = ax.bar(categories, values, color=colors, width=0.6, edgecolor='black', linewidth=2)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{int(height)}\n({height / self.summary["total"] * 100:.1f}%)',
                    ha='center', va='bottom', fontsize=14, fontweight='bold')

        ax.set_ylabel('Number of Test Cases', fontsize=12, fontweight='bold')
        ax.set_title('Authorization Test Results Summary', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylim(0, max(values) * 1.2)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig('visualizations/overall_summary.png', dpi=300, bbox_inches='tight')
        print("✅ Created: visualizations/overall_summary.png")
        plt.close()

    def create_heatmap_by_audience(self):
        """Create heat maps showing ALLOW/DENY patterns for each audience"""
        audiences = ['owner', 'collaborator', 'org_member', 'external']
        visibilities = ['private', 'shared', 'org_public', 'public']
        actions = ['read', 'edit', 'delete', 'share']

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()

        for idx, audience in enumerate(audiences):
            # Filter data for this audience
            audience_data = self.results[self.results['audience'] == audience]

            # Create matrix: rows=actions, cols=visibilities
            matrix = np.zeros((len(actions), len(visibilities)))

            for i, action in enumerate(actions):
                for j, visibility in enumerate(visibilities):
                    row = audience_data[
                        (audience_data['action'] == action) &
                        (audience_data['visibility'] == visibility)
                        ]
                    if len(row) > 0:
                        # 1 = ALLOW, 0 = DENY, -1 = FAILED
                        if row.iloc[0]['passed']:
                            matrix[i][j] = 1 if row.iloc[0]['actual'] == 'ALLOW' else 0
                        else:
                            matrix[i][j] = -1  # Failed test

            # Create heatmap
            ax = axes[idx]

            # Custom colormap: green=ALLOW, red=DENY, orange=FAILED
            colors = ['#F44336', '#FFC107', '#4CAF50']  # red, orange, green
            n_bins = 3
            cmap = sns.color_palette(colors, n_bins)

            sns.heatmap(matrix, annot=True, fmt='.0f', cmap=cmap,
                        xticklabels=visibilities, yticklabels=actions,
                        cbar=False, linewidths=2, linecolor='black',
                        vmin=-1, vmax=1, ax=ax,
                        annot_kws={'size': 12, 'weight': 'bold'})

            # Customize annotations
            for text in ax.texts:
                val = float(text.get_text())
                if val == 1:
                    text.set_text('ALLOW')
                    text.set_color('white')
                elif val == 0:
                    text.set_text('DENY')
                    text.set_color('white')
                elif val == -1:
                    text.set_text('BUG!')
                    text.set_color('black')

            ax.set_title(f'{audience.upper()}', fontsize=14, fontweight='bold', pad=10)
            ax.set_xlabel('File Visibility', fontsize=11, fontweight='bold')
            ax.set_ylabel('Action', fontsize=11, fontweight='bold')

        plt.suptitle('Authorization Matrix by Audience Type',
                     fontsize=18, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig('visualizations/heatmap_by_audience.png', dpi=300, bbox_inches='tight')
        print("✅ Created: visualizations/heatmap_by_audience.png")
        plt.close()

    def create_failures_by_audience(self):
        """Bar chart showing failures by audience type"""
        failures_data = self.results[self.results['passed'] == False]
        audience_counts = failures_data['audience'].value_counts()

        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.bar(audience_counts.index, audience_counts.values,
                      color='#F44336', edgecolor='black', linewidth=2, width=0.6)

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=14, fontweight='bold')

        ax.set_xlabel('Audience Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Failures', fontsize=12, fontweight='bold')
        ax.set_title('Authorization Failures by Audience Type',
                     fontsize=16, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig('visualizations/failures_by_audience.png', dpi=300, bbox_inches='tight')
        print("✅ Created: visualizations/failures_by_audience.png")
        plt.close()

    def create_failures_by_action(self):
        """Bar chart showing failures by action type"""
        failures_data = self.results[self.results['passed'] == False]
        action_counts = failures_data['action'].value_counts()

        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.bar(action_counts.index, action_counts.values,
                      color='#FF5722', edgecolor='black', linewidth=2, width=0.6)

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=14, fontweight='bold')

        ax.set_xlabel('Action Type', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Failures', fontsize=12, fontweight='bold')
        ax.set_title('Authorization Failures by Action Type',
                     fontsize=16, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig('visualizations/failures_by_action.png', dpi=300, bbox_inches='tight')
        print("✅ Created: visualizations/failures_by_action.png")
        plt.close()

    def create_pass_rate_by_audience(self):
        """Stacked bar chart showing pass rate by audience"""
        audiences = ['owner', 'collaborator', 'org_member', 'external']

        pass_counts = []
        fail_counts = []

        for audience in audiences:
            audience_data = self.results[self.results['audience'] == audience]
            passed = len(audience_data[audience_data['passed'] == True])
            failed = len(audience_data[audience_data['passed'] == False])
            pass_counts.append(passed)
            fail_counts.append(failed)

        fig, ax = plt.subplots(figsize=(12, 6))

        x = np.arange(len(audiences))
        width = 0.6

        p1 = ax.bar(x, pass_counts, width, label='Passed',
                    color='#4CAF50', edgecolor='black', linewidth=2)
        p2 = ax.bar(x, fail_counts, width, bottom=pass_counts,
                    label='Failed', color='#F44336', edgecolor='black', linewidth=2)

        # Add percentage labels
        for i, (passed, failed) in enumerate(zip(pass_counts, fail_counts)):
            total = passed + failed
            pass_pct = (passed / total * 100) if total > 0 else 0
            fail_pct = (failed / total * 100) if total > 0 else 0

            # Passed label
            if passed > 0:
                ax.text(i, passed / 2, f'{passed}\n({pass_pct:.0f}%)',
                        ha='center', va='center', fontsize=11, fontweight='bold', color='white')

            # Failed label
            if failed > 0:
                ax.text(i, passed + failed / 2, f'{failed}\n({fail_pct:.0f}%)',
                        ha='center', va='center', fontsize=11, fontweight='bold', color='white')

        ax.set_ylabel('Number of Test Cases', fontsize=12, fontweight='bold')
        ax.set_title('Pass Rate by Audience Type', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(audiences, fontsize=11)
        ax.legend(fontsize=11, loc='upper right')
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        plt.tight_layout()
        plt.savefig('visualizations/pass_rate_by_audience.png', dpi=300, bbox_inches='tight')
        print("✅ Created: visualizations/pass_rate_by_audience.png")
        plt.close()

    def create_severity_matrix(self):
        """Create a matrix showing bug severity (external users = highest)"""
        failures_data = self.results[self.results['passed'] == False]

        # Count failures by audience and visibility
        audiences = ['collaborator', 'org_member', 'external']
        visibilities = ['private', 'shared', 'org_public', 'public']

        matrix = np.zeros((len(audiences), len(visibilities)))

        for i, audience in enumerate(audiences):
            for j, visibility in enumerate(visibilities):
                count = len(failures_data[
                                (failures_data['audience'] == audience) &
                                (failures_data['visibility'] == visibility)
                                ])
                matrix[i][j] = count

        fig, ax = plt.subplots(figsize=(10, 6))

        sns.heatmap(matrix, annot=True, fmt='.0f', cmap='Reds',
                    xticklabels=visibilities, yticklabels=audiences,
                    cbar_kws={'label': 'Number of Bugs'}, linewidths=2, linecolor='black',
                    ax=ax, annot_kws={'size': 14, 'weight': 'bold'})

        ax.set_title('Bug Distribution Matrix (Higher = More Severe)',
                     fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('File Visibility', fontsize=12, fontweight='bold')
        ax.set_ylabel('Audience Type', fontsize=12, fontweight='bold')

        plt.tight_layout()
        plt.savefig('visualizations/severity_matrix.png', dpi=300, bbox_inches='tight')
        print("✅ Created: visualizations/severity_matrix.png")
        plt.close()

    def generate_all_visualizations(self):
        """Generate all visualizations at once"""
        print("\n" + "=" * 60)
        print("GENERATING VISUALIZATIONS")
        print("=" * 60 + "\n")

        self.create_overall_summary()
        self.create_heatmap_by_audience()
        self.create_failures_by_audience()
        self.create_failures_by_action()
        self.create_pass_rate_by_audience()
        self.create_severity_matrix()

        print("\n" + "=" * 60)
        print("✅ ALL VISUALIZATIONS CREATED")
        print("=" * 60)
        print(f"\n📁 Check the 'visualizations/' folder for all charts!\n")


# Main execution
if __name__ == "__main__":
    visualizer = TestResultVisualizer('test_results.json')
    visualizer.generate_all_visualizations()