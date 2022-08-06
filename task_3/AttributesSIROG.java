package org.vadere.state.attributes.models;

import org.vadere.annotation.factories.attributes.ModelAttributeClass;
import org.vadere.state.attributes.Attributes;

@ModelAttributeClass
public class AttributesSIROG extends Attributes {

    // Controls the number of intoxicated pedestrians in the beginning of the simulation.This value can also we controlled using the GUI
    private int intoxicatedAtStart = 0;

    // Controls the number of relieved pedestrians in the beginning of the simulation.This value can also we controlled using the GUI
    private int relievedAtStart = 0;

    // Controls the Relief rate of the pedestrians. This value can also we controlled using the GUI
    private double reliefRate = 0.001;

    // Controls the radius to keep around the obstacle. This value can also we controlled using the GUI
    private double obstacleRadius = 3.0;

    public int getIntoxicatedAtStartAtStart() { return intoxicatedAtStart; }

    public int getRelievedAtStart() { return relievedAtStart; }

    public double getReliefRate() {
        return reliefRate;
    }

    public double getObstacleRadius() { return obstacleRadius; }
}

