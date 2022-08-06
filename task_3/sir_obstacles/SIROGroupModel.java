package org.vadere.simulator.models.groups.sir_obstacles;


import org.vadere.annotation.factories.models.ModelClass;
import org.vadere.simulator.models.Model;
import org.vadere.simulator.models.groups.AbstractGroupModel;
import org.vadere.simulator.models.groups.Group;
import org.vadere.simulator.models.groups.GroupSizeDeterminator;
import org.vadere.simulator.models.groups.sir.SIRGroup;
import org.vadere.simulator.models.groups.sir.SIRType;
import org.vadere.simulator.models.potential.fields.IPotentialFieldTarget;
import org.vadere.simulator.projects.Domain;
import org.vadere.state.attributes.Attributes;
import org.vadere.state.attributes.models.AttributesSIROG;
import org.vadere.state.attributes.scenario.AttributesAgent;
import org.vadere.state.scenario.DynamicElementContainer;
import org.vadere.state.scenario.Pedestrian;
import org.vadere.state.scenario.Topography;
import org.vadere.util.geometry.LinkedCellsGrid;
import org.vadere.state.scenario.Obstacle;
import org.vadere.util.geometry.shapes.VPoint;

import java.util.*;

/**
 * Implementation of groups for a susceptible / infected / removed (SIR) model.
 */
@ModelClass
public class SIROGroupModel extends AbstractGroupModel<SIROGroup> {

	private Random random;
	private LinkedHashMap<Integer, SIROGroup> groupsById;
	private Map<Integer, LinkedList<SIROGroup>> sourceNextGroups;
	private AttributesSIROG attributesSIRG;
	private Topography topography;
	private IPotentialFieldTarget potentialFieldTarget;
	private int totalIntoxicated = 0;
	private int totalRelieved = 0;

	// Record previous time step for decoupling the timestep length from the visualization
	private double prevSimTimeInSec = -0.1;

	// Probability of recovery
	double recoveryProbablity = 0.0005;

	public SIROGroupModel() {
		this.groupsById = new LinkedHashMap<>();
		this.sourceNextGroups = new HashMap<>();
	}

	@Override
	public void initialize(List<Attributes> attributesList, Domain domain,
						   AttributesAgent attributesPedestrian, Random random) {
		this.attributesSIRG = Model.findAttributes(attributesList, AttributesSIROG.class);
		this.topography = domain.getTopography();
		this.random = random;
		this.totalIntoxicated = 0;
		this.totalRelieved = 0;
		this.recoveryProbablity = 0.0005;
	}


	@Override
	public void setPotentialFieldTarget(IPotentialFieldTarget potentialFieldTarget) {
		this.potentialFieldTarget = potentialFieldTarget;
		// update all existing groups
		for (SIROGroup group : groupsById.values()) {
			group.setPotentialFieldTarget(potentialFieldTarget);
		}
	}

	@Override
	public IPotentialFieldTarget getPotentialFieldTarget() {
		return potentialFieldTarget;
	}

	private int getFreeGroupId() {
		if(this.totalIntoxicated < this.attributesSIRG.getIntoxicatedAtStartAtStart()) {
			if(!getGroupsById().containsKey(SIROType.ID_INTOXICATED.ordinal()))
			{
				SIROGroup g = getNewGroup(SIROType.ID_INTOXICATED.ordinal(), Integer.MAX_VALUE/2);
				getGroupsById().put(SIROType.ID_INTOXICATED.ordinal(), g);
			}
			this.totalIntoxicated += 1;
			return SIROType.ID_INTOXICATED.ordinal();
		}

		// Added a new case to add recovered persons in the beginning if required

		else if(
		 	this.totalRelieved < this.attributesSIRG.getRelievedAtStart()){
			if(!getGroupsById().containsKey(SIROType.ID_RELIEVED.ordinal()))
			{
				SIROGroup g = getNewGroup(SIROType.ID_RELIEVED.ordinal(), Integer.MAX_VALUE/2);
				getGroupsById().put(SIROType.ID_RELIEVED.ordinal(), g);
			}
			this.totalRelieved += 1;
			return SIROType.ID_RELIEVED.ordinal();
		}
		else{
			if(!getGroupsById().containsKey(SIROType.ID_SOBER.ordinal()))
			{
				SIROGroup g = getNewGroup(SIROType.ID_SOBER.ordinal(), Integer.MAX_VALUE/2);
				getGroupsById().put(SIROType.ID_SOBER.ordinal(), g);
			}
			return SIROType.ID_SOBER.ordinal();
		}
	}


	@Override
	public void registerGroupSizeDeterminator(int sourceId, GroupSizeDeterminator gsD) {
		sourceNextGroups.put(sourceId, new LinkedList<>());
	}

	@Override
	public int nextGroupForSource(int sourceId) {
		return Integer.MAX_VALUE/2;
	}

	@Override
	public SIROGroup getGroup(final Pedestrian pedestrian) {
		SIROGroup group = groupsById.get(pedestrian.getGroupIds().getFirst());
		assert group != null : "No group found for pedestrian";
		return group;
	}

	@Override
	protected void registerMember(final Pedestrian ped, final SIROGroup group) {
		groupsById.putIfAbsent(ped.getGroupIds().getFirst(), group);
	}

	@Override
	public Map<Integer, SIROGroup> getGroupsById() {
		return groupsById;
	}

	@Override
	protected SIROGroup getNewGroup(final int size) {
		return getNewGroup(getFreeGroupId(), size);
	}

	@Override
	protected SIROGroup getNewGroup(final int id, final int size) {
		if(groupsById.containsKey(id))
		{
			return groupsById.get(id);
		}
		else
		{
			return new SIROGroup(id, this);
		}
	}

	private void initializeGroupsOfInitialPedestrians() {
		// get all pedestrians already in topography
		DynamicElementContainer<Pedestrian> c = topography.getPedestrianDynamicElements();

		if (c.getElements().size() > 0) {
			// Here you can fill in code to assign pedestrians in the scenario at the beginning (i.e., not created by a source)
			//  to INTOXICATED or SOBER groups. This is not required in the exercise though.
		}
	}

	protected void assignToGroup(Pedestrian ped, int groupId) {
		SIROGroup currentGroup = getNewGroup(groupId, Integer.MAX_VALUE/2);
		currentGroup.addMember(ped);
		ped.getGroupIds().clear();
		ped.getGroupSizes().clear();
		ped.addGroupId(currentGroup.getID(), currentGroup.getSize());
		registerMember(ped, currentGroup);
	}

	protected void assignToGroup(Pedestrian ped) {
		int groupId = getFreeGroupId();
		assignToGroup(ped, groupId);
	}


	/* DynamicElement Listeners */

	@Override
	public void elementAdded(Pedestrian pedestrian) {
		assignToGroup(pedestrian);
	}

	@Override
	public void elementRemoved(Pedestrian pedestrian) {
		Group group = groupsById.get(pedestrian.getGroupIds().getFirst());
		if (group.removeMember(pedestrian)) { // if true pedestrian was last member.
			groupsById.remove(group.getID());
		}
	}

	/* Model Interface */

	@Override
	public void preLoop(final double simTimeInSec) {
		initializeGroupsOfInitialPedestrians();
		topography.addElementAddedListener(Pedestrian.class, this);
		topography.addElementRemovedListener(Pedestrian.class, this);
	}

	@Override
	public void postLoop(final double simTimeInSec) {
	}

	@Override
	public void update(final double simTimeInSec) {
		int timeStepLength = (int) Math.round((simTimeInSec - prevSimTimeInSec) * 10);
		// check the positions of all pedestrians and switch groups to INTOXICATED (or REMOVED).
		DynamicElementContainer<Pedestrian> c = topography.getPedestrianDynamicElements();
		double w = topography.getAttributes().getBounds().width;
		double h = topography.getAttributes().getBounds().height;

		// Create grid cell
		LinkedCellsGrid<Pedestrian> linkedCellsGrid =  new LinkedCellsGrid<>(topography.getAttributes().getBounds().x,topography.getAttributes().getBounds().y,
				w,h,w*h);

		// Add pedestrian to grid cells
		if (c.getElements().size() > 0) {
			for (Pedestrian p : c.getElements()) {
				linkedCellsGrid.addObject(p);
			}
		}
		for (int i = 0; i < timeStepLength; i++) {
			for (Pedestrian p : c.getElements()) {
				/*
					 Becoming relieved.
					 If the current pedestrian is intoxicated. We randomly sample a value between 0 and 1 with probability = reliefProbablity.
					 If the value is lesser than the relief rate we mark the pedestrian as relieved.
				 */
				if (getGroup(p).getID() == SIROType.ID_INTOXICATED.ordinal()) {
					if (this.random.nextDouble() + this.recoveryProbablity < attributesSIRG.getReliefRate()) {
						elementRemoved(p);
						assignToGroup(p, SIROType.ID_RELIEVED.ordinal());
						this.totalIntoxicated--;
						this.totalRelieved++;

//						Create obstacle at the relieved position
						VPoint obstacle = p.getPosition();

//						Find pedestrians within the obstacle radius
						List<Pedestrian> neighbors = linkedCellsGrid.getObjects(obstacle, attributesSIRG.getObstacleRadius());
						for (Pedestrian p_neighbor : neighbors) {
							double dist = obstacle.distance(p_neighbor.getPosition());
							if (dist <= attributesSIRG.getObstacleRadius() &&
									p_neighbor.getId() != p.getId() &&
									// Relieved pedestrians don't have to avoid each other
									getGroup(p_neighbor).getID() != SIROType.ID_RELIEVED.ordinal()) {
								// Do not allow to come closer than the obstacle radius allows.
								VPoint neighborPosition = p_neighbor.getPosition();

								// Compute the shift vector and normalize it
								double new_x = neighborPosition.getX() - obstacle.getX();
								double new_y = p_neighbor.getPosition().getY() - obstacle.getY();
								double norm = Math.sqrt(Math.pow(new_x, 2) + Math.pow(new_y, 2));
								new_x = new_x / norm / 5.0;
								new_y = new_y / norm / 5.0;
								// Shift the neighbour outside the radius
								VPoint shiftedPos = new VPoint(neighborPosition.getX() + new_x, neighborPosition.getY() + new_y);
								p_neighbor.setPosition(shiftedPos);
							}
						}
						continue;
					}
				}
			}
		}

		prevSimTimeInSec = simTimeInSec;
	}
}