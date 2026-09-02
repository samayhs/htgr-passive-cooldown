{
    // Temperature-based solid energy equation (replaces the stock enthalpy form).
    //
    //     rho*Cp(T) dT/dt = div(kappa(T) grad T) + q'''
    //
    // Solving directly in T removes the variable-Cp bias of the enthalpy solver:
    // the stock form div(alpha grad h), alpha=kappa/Cp, inserts Cp as a nodal value
    // in alpha but as an interval-mean in grad h, and the two cancel only for
    // constant Cp -- leaving a mesh-independent offset (~17 C here). In the T form,
    // steady conduction div(kappa grad T)+q'''=0 is Cp-INDEPENDENT (correct by
    // construction), and Cp(T) enters ONLY the transient inertia term, where it
    // physically belongs. For a steadyState ddt scheme the ddt term is identically
    // zero, so the steady result carries no Cp dependence at all.
    //
    // We solve on thermo.T() in place so the coupled interface BC (which exchanges
    // temperature + kappa) updates directly; the enthalpy field is resynced to the
    // new T afterwards so the thermo state (he, rho, alpha) stays consistent.
    volScalarField& T = const_cast<volScalarField&>(thermo.T());

    while (pimple.correctNonOrthogonal())
    {
        fvScalarMatrix TEqn
        (
            fvm::ddt(betav*rho*cp, T)
          - fvm::laplacian(betav*kappa, T, "laplacian(alpha,h)")
          ==
            betav*Q            // volumetric fission heat [W/m^3] (see setRegionSolidFields.H)
        );

        TEqn.relax();

        fvOptions.constrain(TEqn);

        TEqn.solve();

        fvOptions.correct(T);
    }

    // Resync enthalpy to the solved temperature, then update rho/alpha via the
    // thermo (its calculate() inverts he->T, which returns the same T).
    h = thermo.he(p, T);
}

thermo.correct();

Info<< "Min/max T:" << min(thermo.T()).value() << ' '
    << max(thermo.T()).value() << endl;

// --- Phase-1 energy monitor -------------------------------------------------
// Writes, each solid solve, the exact solver-side energy terms for the transient
// conservation check  d(int rho*h)/dt = P_decay - Q_out:
//   U     = int rho*h dV            (total sensible enthalpy [J])
//   Pdec  = int Q dV                (decay power in [W])
//   Qout  = int -kappa*snGrad(T) dA over outerWall (conductive flux out = radiated [W])
// Appends "time U Pdec Qout" to <case>/solidEnergy.dat (dedupe by time in post).
{
    const fvMesh& monMesh = thermo.T().mesh();
    const scalarField& Vc = monMesh.V();                       // cell volumes
    const scalar Utot = gSum(rho.primitiveField()*h.primitiveField()*Vc);  // int rho*h dV [J]
    const scalar Pdec = gSum(Q.primitiveField()*Vc);           // int Q dV [W]
    scalar Qout = 0.0;
    const label patchi = monMesh.boundaryMesh().findPatchID("outerWall");
    if (patchi != -1)
    {
        Qout = -gSum
        (
            kappa.boundaryField()[patchi]
          * thermo.T().boundaryField()[patchi].snGrad()
          * monMesh.magSf().boundaryField()[patchi]
        );
    }
    // master-only line to the log; grep "ENERGYMON" and dedupe by time in post
    Info<< "ENERGYMON " << monMesh.time().value() << ' ' << Utot << ' '
        << Pdec << ' ' << Qout << endl;
}
