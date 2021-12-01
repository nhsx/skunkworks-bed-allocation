import jax.numpy as jnp
import numpyro.distributions as dist
from numpyro import deterministic, plate, sample


def spectral_density(
    w: jnp.ndarray, alpha: jnp.ndarray, length: jnp.ndarray
) -> jnp.ndarray:
    c = alpha * jnp.sqrt(2 * jnp.pi) * length
    e = jnp.exp(-0.5 * (length ** 2) * (w ** 2))
    return c * e


def diag_spectral_density(
    alpha: jnp.ndarray, length: jnp.ndarray, L: float, M: int
) -> jnp.ndarray:
    """spd for squared exponential kernel."""
    sqrt_eigenvalues = jnp.arange(1, 1 + M) * jnp.pi / 2 / L
    return spectral_density(sqrt_eigenvalues, alpha, length)


def phi(x: jnp.ndarray, L: float, M: int) -> jnp.ndarray:
    """
    The first `M` eigenfunctions of the laplacian operator in `[-L, L]`
    evaluated at `x`. These are used for the approximation of the
    squared exponential kernel.
    """
    m1 = (jnp.pi / (2 * L)) * jnp.tile(L + x[:, None], M)
    m2 = jnp.diag(jnp.linspace(1, M, num=M))
    num = jnp.sin(m1 @ m2)
    den = jnp.sqrt(L)
    return num / den


def gp(
    x: jnp.ndarray,
    day_of_week: jnp.ndarray,
    hour_of_day: jnp.ndarray,
    is_holiday: jnp.ndarray,
    L: float,
    M: int,
    y: jnp.ndarray = None,
):
    """
    Long term trend captured using a Gaussian Process (GP), inspired by 
    previous work of Vehtari et al., as summarised in this blog post:
    https://avehtari.github.io/casestudies/Birthdays/birthdays.html#Load_and_plot_data

    In practice, GPs can be inefficient to calculate, so the Hilbert Space 
    approximation based on this numpyro tutorial was used to ensure tractable 
    runtimes:
    http://num.pyro.ai/en/latest/examples/hsgp.html
    """

    # Intercept
    intercept = sample("intercept", dist.Normal(2.0, 1))

    # Long term trend
    ρ = sample("ρ", dist.Gamma(2, 5))
    α = sample("α", dist.HalfNormal(1.0))
    eigenfunctions = phi(x, L, M)
    spd = jnp.sqrt(diag_spectral_density(α, ρ, L, M))
    with plate("basis1", M):
        β1 = sample("β1", dist.Normal(0, 1))

    f1 = deterministic("f1", eigenfunctions @ (spd * β1))

    # Day of week effect
    with plate("plate_day_of_week", 6):
        _β_week = sample("_β_week", dist.Normal(0, 1))

    β_week = jnp.concatenate([jnp.array([-jnp.sum(_β_week)]), _β_week])
    deterministic("β_week", β_week)

    # Hour of day of effect
    with plate("plate_hour_of_day", 23):
        _β_hour = sample("_β_hour", dist.Normal(0, 1))

    β_hour = jnp.concatenate([jnp.array([-jnp.sum(_β_hour)]), _β_hour])
    deterministic("β_hour", β_hour)

    # Holiday effect, assume all holidays behave like sundays
    β_holiday = β_week[6]

    day_effect = jnp.where(is_holiday, β_holiday, β_week[day_of_week])

    # Combine
    μ = deterministic("μ", intercept + f1 + day_effect + β_hour[hour_of_day])
    σ = sample("σ", dist.HalfNormal(0.5))
    with plate("n_obs", x.shape[0]):
        sample(
            "y",
            dist.NegativeBinomial2(jnp.exp(μ), concentration=1.0 / σ),
            obs=y,
        )
