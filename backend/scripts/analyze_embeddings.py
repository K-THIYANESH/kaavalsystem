"""
KAAVAL Embedding Analysis and Visualization Tools
Provides utilities to analyze and visualize extracted embeddings.
"""
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import seaborn as sns


def load_embeddings(embeddings_dir: Path) -> Dict[str, np.ndarray]:
    """Load all embeddings from the output directory.
    
    Args:
        embeddings_dir: Directory containing embedding files
        
    Returns:
        Dictionary mapping person names to their embedding arrays
    """
    embeddings = {}
    
    # Load NumPy files
    for npy_file in embeddings_dir.glob("*_embeddings.npy"):
        person_name = npy_file.stem.replace("_embeddings", "")
        embeddings[person_name] = np.load(npy_file)
    
    return embeddings


def compute_embedding_statistics(embeddings: Dict[str, np.ndarray]) -> Dict:
    """Compute statistics for embeddings.
    
    Args:
        embeddings: Dictionary of person embeddings
        
    Returns:
        Dictionary containing statistics
    """
    stats = {
        'total_persons': len(embeddings),
        'total_embeddings': sum(len(emb) for emb in embeddings.values()),
        'embedding_dimension': None,
        'persons': {}
    }
    
    for person_name, person_embeddings in embeddings.items():
        if stats['embedding_dimension'] is None and len(person_embeddings) > 0:
            stats['embedding_dimension'] = person_embeddings.shape[1]
        
        # Compute per-person statistics
        if len(person_embeddings) > 0:
            mean_embedding = np.mean(person_embeddings, axis=0)
            std_embedding = np.std(person_embeddings, axis=0)
            
            # Compute pairwise similarities within person
            similarities = []
            for i in range(len(person_embeddings)):
                for j in range(i+1, len(person_embeddings)):
                    sim = np.dot(person_embeddings[i], person_embeddings[j])
                    similarities.append(sim)
            
            stats['persons'][person_name] = {
                'num_embeddings': len(person_embeddings),
                'mean_norm': float(np.mean(np.linalg.norm(person_embeddings, axis=1))),
                'std_norm': float(np.std(np.linalg.norm(person_embeddings, axis=1))),
                'intra_person_similarity': {
                    'mean': float(np.mean(similarities)) if similarities else 0.0,
                    'std': float(np.std(similarities)) if similarities else 0.0,
                    'min': float(np.min(similarities)) if similarities else 0.0,
                    'max': float(np.max(similarities)) if similarities else 0.0
                }
            }
    
    return stats


def visualize_embeddings_2d(
    embeddings: Dict[str, np.ndarray],
    output_path: Path,
    method: str = 'pca'
) -> None:
    """Visualize embeddings in 2D using dimensionality reduction.
    
    Args:
        embeddings: Dictionary of person embeddings
        output_path: Path to save the visualization
        method: 'pca' or 'tsne'
    """
    # Prepare data
    all_embeddings = []
    labels = []
    colors = []
    
    color_palette = sns.color_palette("husl", len(embeddings))
    
    for idx, (person_name, person_embeddings) in enumerate(embeddings.items()):
        all_embeddings.append(person_embeddings)
        labels.extend([person_name] * len(person_embeddings))
        colors.extend([color_palette[idx]] * len(person_embeddings))
    
    all_embeddings = np.vstack(all_embeddings)
    
    # Apply dimensionality reduction
    if method == 'pca':
        reducer = PCA(n_components=2)
        embeddings_2d = reducer.fit_transform(all_embeddings)
        title = f'PCA Visualization of Face Embeddings\n(Explained variance: {sum(reducer.explained_variance_ratio_):.2%})'
    else:  # tsne
        reducer = TSNE(n_components=2, random_state=42, perplexity=min(30, len(all_embeddings)-1))
        embeddings_2d = reducer.fit_transform(all_embeddings)
        title = 't-SNE Visualization of Face Embeddings'
    
    # Create plot
    plt.figure(figsize=(12, 8))
    
    # Plot each person's embeddings
    for idx, (person_name, _) in enumerate(embeddings.items()):
        mask = np.array(labels) == person_name
        plt.scatter(
            embeddings_2d[mask, 0],
            embeddings_2d[mask, 1],
            c=[color_palette[idx]],
            label=person_name.replace('_', ' ').title(),
            alpha=0.6,
            s=100
        )
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Component 1', fontsize=12)
    plt.ylabel('Component 2', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Saved visualization: {output_path}")
    plt.close()


def compute_similarity_matrix(embeddings: Dict[str, np.ndarray]) -> Tuple[np.ndarray, List[str]]:
    """Compute average similarity matrix between all persons.
    
    Args:
        embeddings: Dictionary of person embeddings
        
    Returns:
        Tuple of (similarity matrix, person names)
    """
    person_names = list(embeddings.keys())
    n_persons = len(person_names)
    similarity_matrix = np.zeros((n_persons, n_persons))
    
    for i, person1 in enumerate(person_names):
        for j, person2 in enumerate(person_names):
            # Compute average similarity between all pairs
            emb1 = embeddings[person1]
            emb2 = embeddings[person2]
            
            similarities = []
            for e1 in emb1:
                for e2 in emb2:
                    sim = np.dot(e1, e2)
                    similarities.append(sim)
            
            similarity_matrix[i, j] = np.mean(similarities)
    
    return similarity_matrix, person_names


def visualize_similarity_matrix(
    similarity_matrix: np.ndarray,
    person_names: List[str],
    output_path: Path
) -> None:
    """Visualize the similarity matrix as a heatmap.
    
    Args:
        similarity_matrix: NxN similarity matrix
        person_names: List of person names
        output_path: Path to save the visualization
    """
    plt.figure(figsize=(10, 8))
    
    # Format person names
    formatted_names = [name.replace('_', ' ').title() for name in person_names]
    
    sns.heatmap(
        similarity_matrix,
        xticklabels=formatted_names,
        yticklabels=formatted_names,
        annot=True,
        fmt='.3f',
        cmap='RdYlGn',
        center=0.5,
        vmin=0,
        vmax=1,
        square=True,
        cbar_kws={'label': 'Cosine Similarity'}
    )
    
    plt.title('Average Inter-Person Similarity Matrix', fontsize=14, fontweight='bold')
    plt.xlabel('Person', fontsize=12)
    plt.ylabel('Person', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Saved similarity matrix: {output_path}")
    plt.close()


def analyze_embeddings(embeddings_dir: Path, output_dir: Path) -> None:
    """Run complete analysis on extracted embeddings.
    
    Args:
        embeddings_dir: Directory containing embedding files
        output_dir: Directory to save analysis results
    """
    print("="*60)
    print("KAAVAL EMBEDDING ANALYSIS")
    print("="*60)
    
    # Load embeddings
    print("\n📂 Loading embeddings...")
    embeddings = load_embeddings(embeddings_dir)
    print(f"✅ Loaded embeddings for {len(embeddings)} persons")
    
    # Compute statistics
    print("\n📊 Computing statistics...")
    stats = compute_embedding_statistics(embeddings)
    
    # Save statistics
    output_dir.mkdir(parents=True, exist_ok=True)
    stats_path = output_dir / "embedding_statistics.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"💾 Saved statistics: {stats_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("STATISTICS SUMMARY")
    print("="*60)
    print(f"Total Persons:      {stats['total_persons']}")
    print(f"Total Embeddings:   {stats['total_embeddings']}")
    print(f"Embedding Dim:      {stats['embedding_dimension']}")
    print("\nPer-Person Statistics:")
    for person_name, person_stats in stats['persons'].items():
        print(f"\n  {person_name.replace('_', ' ').title()}:")
        print(f"    Embeddings:     {person_stats['num_embeddings']}")
        print(f"    Avg Norm:       {person_stats['mean_norm']:.4f}")
        print(f"    Intra-Sim:      {person_stats['intra_person_similarity']['mean']:.4f} "
              f"± {person_stats['intra_person_similarity']['std']:.4f}")
    
    # Create visualizations
    print("\n📊 Creating visualizations...")
    
    # PCA visualization
    pca_path = output_dir / "embeddings_pca.png"
    visualize_embeddings_2d(embeddings, pca_path, method='pca')
    
    # t-SNE visualization
    tsne_path = output_dir / "embeddings_tsne.png"
    visualize_embeddings_2d(embeddings, tsne_path, method='tsne')
    
    # Similarity matrix
    sim_matrix, person_names = compute_similarity_matrix(embeddings)
    sim_matrix_path = output_dir / "similarity_matrix.png"
    visualize_similarity_matrix(sim_matrix, person_names, sim_matrix_path)
    
    print("\n" + "="*60)
    print("✅ Analysis complete!")
    print("="*60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analyze extracted face embeddings"
    )
    parser.add_argument(
        '--embeddings-dir',
        type=str,
        required=True,
        help='Directory containing extracted embeddings'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Directory to save analysis results (default: embeddings_dir/analysis)'
    )
    
    args = parser.parse_args()
    
    embeddings_dir = Path(args.embeddings_dir)
    output_dir = Path(args.output_dir) if args.output_dir else embeddings_dir / "analysis"
    
    analyze_embeddings(embeddings_dir, output_dir)


if __name__ == "__main__":
    main()
